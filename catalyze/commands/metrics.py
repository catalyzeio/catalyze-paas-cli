from __future__ import absolute_import

import click
import sys
import json
import time
import math
import sparkline
import csv
from StringIO import StringIO
from catalyze import cli, client, project, output
from catalyze.helpers import environments, services

@cli.command("metrics", short_help = "Get service metrics")
@click.argument("service_label", required = False, default = None)
@click.option("--format", help = "Output in a special format. Accepted values are 'csv', 'json', 'spark'.")
@click.option("--stream", is_flag = True, default = False, help = "Repeat calls once per minute until this process is interrupted.")
@click.option("--mins", type = int, default = 1, help = "How many minutes' worth of logs to retrieve.")
def metrics(service_label, format, stream, mins):
    """Print out metrics about a single service or all services in an environment."""
    if stream and (format or mins != 1):
        output.error("--stream cannot be used with a custom format or multiple records.")

    if format is None:
        transformer = TextTransformer()
    elif format == "csv":
        transformer = CSVTransformer()
    elif format == "json":
        transformer = JSONTransformer()
    elif format == "spark":
        transformer = SparkTransformer()
        mins = 60
    else:
        output.error("unrecognized format '%s'" % (format,))

    settings = project.read_settings()
    session = client.acquire_session(settings)

    if service_label is None:
        transformer.set_group_mode()
        transformer.set_retriever(lambda: environments.retrieve_metrics(session, settings["environmentId"], mins))
    else:
        service_id = services.get_by_label(session, settings["environmentId"], service_label)
        transformer.set_retriever(lambda: services.retrieve_metrics(session, settings["environmentId"], service_id, mins))

    transformer.process(stream)

class MetricsTransformer:
    def __init__(self):
        self.group_mode = False
        self.retriever = lambda: {}

    def set_group_mode(self):
        self.group_mode = True

    def set_retriever(self, func):
        self.retriever = func

    def process(self, poll):
        while True:
            self.transform(self.retriever())
            if not poll:
                break
            time.sleep(60)

    def transform(self, data):
        if self.group_mode:
            self.transform_group(data)
        else:
            self.transform_single(data["jobs"])

    def transform_single(self, data):
        pass

    def transform_group(self, data):
        pass

class TextTransformer(MetricsTransformer):
    def transform_single(self, data, prefix = ""):
        for job in data:
            for metric in job["metrics"]:
                output.write("%s%s | %8s (%s) | CPU: %6.2fs (%5.2f%%) | Net: RX: %d KB TX: %d KB | Mem: %d KB | Disk: %d KB read / %d KB write " % ( \
                    prefix, \
                    time.strftime("%Y-%m-%d %H:%M:%S", time.gmtime(metric["ts"])), \
                    job["type"], \
                    job["id"], \
                    metric["cpu"]["usage"] / 1000000000.0, \
                    metric["cpu"]["usage"] / 1000000000.0 / 60.0 * 100.0,
                    math.ceil(metric["network"]["rx_bytes"]["ave"] / 1024.0), \
                    math.ceil(metric["network"]["tx_bytes"]["ave"] / 1024.0), \
                    math.ceil(metric["memory"]["ave"] / 1024.0),
                    math.ceil(metric["diskio"]["read"] / 1024.0),
                    math.ceil(metric["diskio"]["write"] / 1024.0)))

    def transform_group(self, data):
        for service in data:
            output.write(service["serviceName"] + ":")
            self.transform_single(service["jobs"], prefix = "    ")

class JSONTransformer(MetricsTransformer):
    def transform_single(self, data):
        output.write(json.dumps(data))

    def transform_group(self, data):
        output.write(json.dumps(data))

class CSVTransformer(MetricsTransformer):
    def __init__(self):
        MetricsTransformer.__init__(self)
        self.headers_printed = False
        self.sio = StringIO()
        self.writer = csv.writer(self.sio)

    def write_headers_maybe(self):
        if not self.headers_printed:
            base_headers = ["timestamp", "type", "job_id", "cpu_usage", "rx_bytes", "tx_bytes", "memory", "disk_read", "disk_write"]
            headers = base_headers if not self.group_mode else ["service_label", "service_id"] + base_headers
            self.writer.writerow(headers)
            self.headers_printed = True

    def transform_single(self, data, service_id = None, service_label = None):
        self.write_headers_maybe()
        for job in data:
            for metric in job["metrics"]:
                row = [metric["ts"], \
                        job["type"], \
                        job["id"], \
                        math.ceil(metric["cpu"]["usage"]), \
                        math.ceil(metric["network"]["rx_bytes"]["ave"] / 1024), \
                        math.ceil(metric["network"]["tx_bytes"]["ave"] / 1024), \
                        math.ceil(metric["memory"]["ave"] / 1024.0), \
                        math.ceil(metric["diskio"]["read"] / 1024.0), \
                        math.ceil(metric["diskio"]["write"] / 1024.0)]
                row = row if service_id is None else [service_label, service_id] + row
                self.writer.writerow(row)
        if service_id is None:
            output.write(self.sio.getvalue())

    def transform_group(self, data):
        self.write_headers_maybe()
        for service in data:
            self.transform_single(service["jobs"], service["serviceId"], service["serviceName"])
        output.write(self.sio.getvalue())

def deltas(l): 
    """
    Compute the change between each datapoint.  Since there will be n-1 deltas, 
    add a zero to the front.  While not perfectly accurate, the leading zero
    sets the minimum to always be zero.
    """
     if l:
        return [0] + [j-i for i,j in  zip(l[:-1], l[1:])]
     else:
        return []

class SparkTransformer(MetricsTransformer):
    def transform_single(self, data, prefix = ""):
        for job in data:
            metrics_reversed = job["metrics"][::-1]
            sparkdata = {}
            sparkdata["CPU"] = [metric["cpu"]["usage"]/1000000000.0/60.0*100.0 for metric in metrics_reversed]
            sparkdata["Memory"] =  [metric["memory"]["ave"] for metric in metrics_reversed]
            sparkdata["Net RX"] = deltas([metric["network"]["rx_bytes"]["ave"] for metric in metrics_reversed])
            sparkdata["Net TX"] = deltas([metric["network"]["tx_bytes"]["ave"] for metric in metrics_reversed])
            sparkdata["Disk Read"] = [metric["diskio"]["read"] for metric in metrics_reversed]
            sparkdata["Disk Write"] = [metric["diskio"]["write"] for metric in metrics_reversed]

            for k in sorted(sparkdata.keys()):
                v  = sparkdata[k]
                if v:
                    spark = sparkline.sparkify(v).encode('utf-8')
                    output.write("{}{:>10}: {} min: {} max: {}".format(prefix,k,spark,min(v),max(v)))

    def transform_group(self, data):
        for service in data:
            output.write(service["serviceName"] + ":")
            self.transform_single(service["jobs"], prefix = "    ")

