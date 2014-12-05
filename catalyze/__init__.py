from __future__ import absolute_import

cli = None

def init_cli():
    import click
    from . import config

    @click.group("catalyze")
    @click.option("--baas-host", help = "Alternate BaaS API URL")
    @click.option("--paas-host", help = "Alternate PaaS API URL")
    @click.option("--skip-validation", is_flag = True, help = "Skip certificate validation")
    def inner_cli(baas_host, paas_host, skip_validation):
        if baas_host is not None:
            config.baas_host = baas_host
            print("Overriding BaaS URL: " + config.baas_host)
        if paas_host is not None:
            config.paas_host = paas_host
            print("Overriding PaaS URL: " + config.paas_host)
        if skip_validation:
            config.behavior["skip_cert_validation"] = False
            print("Skipping cert validation, I hope this was intentional")

    global cli
    cli = inner_cli

    @cli.command()
    def version():
        """Outputs the current CLI version."""
        print(config.version)

    from catalyze.commands import \
        associate, dashboard, environments, rake, redeploy, status, variables

def run():
    import catalyze.__main__
