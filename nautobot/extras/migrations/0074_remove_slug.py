# Generated by Django 3.2.18 on 2023-03-15 12:27

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ("ipam", "0027_remove_rir_slug"),
        ("dcim", "0039_remove_slug"),
        ("circuits", "0015_remove_circuittype_provider_slug"),
        ("tenancy", "0007_remove_tenant_tenantgroup_slug"),
        ("virtualization", "0020_remove_clustergroup_clustertype_slug"),
        ("extras", "0073_remove_gitrepository_fields"),
    ]

    operations = [
        migrations.AlterModelOptions(
            name="graphqlquery",
            options={"ordering": ("name",), "verbose_name": "GraphQL query", "verbose_name_plural": "GraphQL queries"},
        ),
        migrations.RemoveField(
            model_name="dynamicgroup",
            name="slug",
        ),
        migrations.RemoveField(
            model_name="graphqlquery",
            name="slug",
        ),
        migrations.RemoveField(
            model_name="jobhook",
            name="slug",
        ),
        migrations.RemoveField(
            model_name="role",
            name="slug",
        ),
        migrations.RemoveField(
            model_name="secret",
            name="slug",
        ),
        migrations.RemoveField(
            model_name="secretsgroup",
            name="slug",
        ),
        migrations.RemoveField(
            model_name="status",
            name="slug",
        ),
    ]
