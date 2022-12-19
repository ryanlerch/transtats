# Copyright 2016 Red Hat, Inc.
# All Rights Reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License"); you may
# not use this file except in compliance with the License. You may obtain
# a copy of the License at
#
# http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
# WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
# License for the specific language governing permissions and limitations
# under the License.

# python
from uuid import uuid4

# django
from django.conf import settings
from django.contrib.postgres.fields import JSONField, ArrayField
from django.db.models.signals import post_save
from django.db import models
from django.dispatch import receiver
from django.utils import timezone

# third party
from rest_framework.authtoken.models import Token


TABLE_PREFIX = 'ts_'


class Languages(models.Model):
    """Languages Model"""
    locale_id = models.CharField(
        max_length=50, primary_key=True, verbose_name="Locale ID"
    )
    lang_name = models.CharField(
        max_length=400, unique=True, verbose_name="Language Name"
    )
    locale_alias = models.CharField(
        max_length=50, unique=True, null=True, blank=True, verbose_name="Locale Alias"
    )
    locale_script = models.CharField(
        max_length=100, null=True, blank=True, verbose_name="Locale Script"
    )
    lang_status = models.BooleanField(verbose_name="Enable/Disable")

    def __str__(self):
        return self.lang_name

    class Meta:
        db_table = TABLE_PREFIX + 'locales'
        verbose_name = "Language"


class LanguageSet(models.Model):
    """Language Set Model"""
    lang_set_id = models.AutoField(primary_key=True)
    lang_set_name = models.CharField(
        max_length=1000, verbose_name="Language Set Name"
    )
    lang_set_slug = models.CharField(
        max_length=400, unique=True, verbose_name="Language Set SLUG"
    )
    lang_set_color = models.CharField(
        max_length=100, unique=True, verbose_name="Tag Colour"
    )
    locale_ids = ArrayField(
        models.CharField(max_length=50, blank=True),
        default=list, null=True, verbose_name="Locale IDs"
    )

    def __str__(self):
        return self.lang_set_name

    class Meta:
        db_table = TABLE_PREFIX + 'langset'
        verbose_name = "Language Set"


class TransPlatform(models.Model):
    """Translation Platforms Model"""
    platform_id = models.AutoField(primary_key=True)
    engine_name = models.CharField(
        max_length=200, verbose_name="Platform Engine"
    )
    subject = models.CharField(
        max_length=200, null=True, verbose_name="Platform Subject"
    )
    api_url = models.URLField(max_length=500, unique=True, verbose_name="Server URL")
    platform_slug = models.CharField(
        max_length=400, unique=True, verbose_name="Platform SLUG"
    )
    server_status = models.BooleanField(verbose_name="Enable/Disable")
    projects_json = JSONField(null=True)
    projects_lastupdated = models.DateTimeField(null=True)
    auth_login_id = models.CharField(
        max_length=200, null=True, blank=True, verbose_name="Auth User"
    )
    auth_token_key = models.CharField(
        max_length=200, null=True, blank=True, verbose_name="Auth Token"
    )

    def __str__(self):
        return "{0} {1}".format(self.engine_name, self.subject)

    class Meta:
        db_table = TABLE_PREFIX + 'transplatforms'
        verbose_name = "Translation Platform"


class ReleaseStream(models.Model):
    """Release Stream Model"""
    relstream_id = models.AutoField(primary_key=True)
    relstream_name = models.CharField(
        max_length=200, verbose_name="Release Stream Name"
    )
    relstream_slug = models.CharField(
        max_length=400, unique=True, verbose_name="Release Stream SLUG"
    )
    relstream_server = models.URLField(
        max_length=500, unique=True, verbose_name="Release Stream Server"
    )
    relstream_built = models.CharField(
        max_length=200, null=True, verbose_name="Release Build System"
    )
    relstream_built_tags = ArrayField(
        models.CharField(max_length=200, blank=True),
        default=list, null=True, verbose_name="Release Build Tags"
    )
    relstream_built_tags_lastupdated = models.DateTimeField(null=True)
    srcpkg_format = models.CharField(
        max_length=50, null=True, verbose_name="Source Package Format"
    )
    top_url = models.URLField(max_length=500, unique=True, verbose_name="Top URL")
    web_url = models.URLField(max_length=500, unique=True, null=True, verbose_name="Web URL")
    krb_service = models.CharField(
        max_length=200, null=True, blank=True, verbose_name="Kerberos Service"
    )
    auth_type = models.CharField(max_length=200, null=True, blank=True, verbose_name="Auth Type")
    amqp_server = models.CharField(
        max_length=500, null=True, blank=True, verbose_name="AMQP Server"
    )
    msgbus_exchange = models.CharField(
        max_length=200, null=True, blank=True, verbose_name="Message Bus Exchange"
    )
    major_milestones = ArrayField(
        models.CharField(max_length=1000, blank=True),
        default=list, null=True, verbose_name="Major Milestones"
    )
    relstream_phases = ArrayField(
        models.CharField(max_length=200, blank=True),
        default=list, null=True, verbose_name="Release Stream Phases"
    )
    relstream_status = models.BooleanField(verbose_name="Enable/Disable")

    def __str__(self):
        return self.relstream_name

    class Meta:
        db_table = TABLE_PREFIX + 'relstreams'
        verbose_name = "Release Stream"


class StreamBranches(models.Model):
    """Stream Branches Model"""
    relbranch_id = models.AutoField(primary_key=True)
    relbranch_name = models.CharField(max_length=500, verbose_name="Release Branch Name")
    relbranch_slug = models.CharField(max_length=500, unique=True, verbose_name="Release Branch Slug")
    relstream_slug = models.CharField(max_length=400, verbose_name="Release Stream Slug")
    lang_set = models.CharField(max_length=200, verbose_name="Language Set")
    scm_branch = models.CharField(max_length=100, null=True, blank=True, verbose_name="SCM Branch Name")
    created_on = models.DateTimeField()
    current_phase = models.CharField(max_length=200, null=True, verbose_name="Current Phase")
    calendar_url = models.URLField(max_length=500, unique=True, null=True, verbose_name="Calender iCal URL")
    schedule_json = JSONField(null=True)
    sync_calendar = models.BooleanField(default=True, verbose_name="Sync Calender")
    notifications_flag = models.BooleanField(default=True, verbose_name="Notification")
    track_trans_flag = models.BooleanField(default=True, verbose_name="Track Translation")
    created_by = models.EmailField(null=True)

    def __str__(self):
        return self.relbranch_name

    class Meta:
        db_table = TABLE_PREFIX + 'relbranches'
        verbose_name_plural = "Release Branches"


class Packages(models.Model):
    """Packages Model"""
    package_id = models.AutoField(primary_key=True)
    package_name = models.CharField(max_length=1000, unique=True, verbose_name="Package Name")
    upstream_name = models.CharField(max_length=1000, null=True, blank=True,
                                     verbose_name="Upstream Name")
    component = models.CharField(max_length=200, null=True, blank=True, verbose_name="Component")
    upstream_url = models.URLField(max_length=2000, unique=True, verbose_name="Upstream URL")
    transplatform_slug = models.ForeignKey(
        TransPlatform, on_delete=models.PROTECT,
        to_field='platform_slug', verbose_name="Translation Platform"
    )
    transplatform_name = models.CharField(max_length=1000, null=True, blank=True,
                                          verbose_name="Package Name at Translation Platform")
    # translation platform project http url
    transplatform_url = models.URLField(max_length=500, null=True, blank=True,
                                        verbose_name="Translation Platform Project URL")
    release_streams = ArrayField(
        models.CharField(max_length=400, blank=True),
        default=list, null=True, verbose_name="Release Streams"
    )
    package_details_json = JSONField(null=True)
    details_json_lastupdated = models.DateTimeField(null=True)
    package_name_mapping = JSONField(null=True)
    release_branch_mapping = JSONField(null=True, blank=True)
    mapping_lastupdated = models.DateTimeField(null=True, blank=True)
    stats_diff = JSONField(null=True, blank=True)
    transtats_lastupdated = models.DateTimeField(null=True, blank=True)
    upstream_latest_stats = JSONField(null=True, blank=True)
    upstream_lastupdated = models.DateTimeField(null=True, blank=True)
    downstream_lastupdated = models.DateTimeField(null=True, blank=True)
    translation_file_ext = models.CharField(
        max_length=10, null=True, blank=True, default='po',
        verbose_name="Translation Format (po)"
    )
    created_by = models.EmailField(null=True)
    maintainers = JSONField(null=True, blank=True)

    def __str__(self):
        return self.package_name

    class Meta:
        db_table = TABLE_PREFIX + 'packages'
        verbose_name = "Package"


class JobTemplates(models.Model):
    """Job Templates Model"""
    job_template_id = models.AutoField(primary_key=True)
    job_template_type = models.CharField(max_length=100, unique=True)
    job_template_name = models.CharField(max_length=500)
    job_template_desc = models.CharField(max_length=1000, blank=True, null=True)
    job_template_params = ArrayField(
        models.CharField(max_length=1000, blank=True), default=list
    )
    job_template_json = JSONField(null=True)
    job_template_last_accessed = models.DateTimeField(null=True)

    def __str__(self):
        return self.job_template_name

    class Meta:
        db_table = TABLE_PREFIX + 'jobtemplates'
        verbose_name = "Job Templates"


class Jobs(models.Model):
    """Jobs Model"""
    job_id = models.AutoField(primary_key=True)
    job_uuid = models.UUIDField(default=uuid4, editable=False)
    job_type = models.CharField(max_length=200)
    job_start_time = models.DateTimeField()
    job_end_time = models.DateTimeField(null=True)
    job_yml_text = models.CharField(max_length=2000, null=True, blank=True)
    job_log_json = JSONField(null=True)
    job_result = models.NullBooleanField()
    job_remarks = models.CharField(max_length=200, null=True)
    job_template = models.ForeignKey(JobTemplates, on_delete=models.PROTECT,
                                     verbose_name="Job Template", null=True)
    job_params_json = JSONField(null=True)
    job_output_json = JSONField(null=True)
    triggered_by = models.EmailField(null=True)
    job_visible_on_url = models.BooleanField(default=False)

    @property
    def duration(self):
        timediff = self.job_end_time - self.job_start_time
        return timediff.total_seconds()

    class Meta:
        db_table = TABLE_PREFIX + 'jobs'


class SyncStats(models.Model):
    """Sync Stats Model"""
    sync_id = models.AutoField(primary_key=True)
    package_name = models.CharField(max_length=500)
    job_uuid = models.UUIDField()
    project_version = models.CharField(max_length=500, null=True)
    source = models.CharField(max_length=500, null=True)
    stats_raw_json = JSONField(null=True)
    stats_processed_json = JSONField(null=True)
    sync_iter_count = models.IntegerField()
    sync_visibility = models.BooleanField()

    class Meta:
        db_table = TABLE_PREFIX + 'syncstats'


class GraphRules(models.Model):
    """Graph Rules Model"""
    graph_rule_id = models.AutoField(primary_key=True)
    rule_name = models.CharField(max_length=1000, unique=True)
    rule_packages = ArrayField(
        models.CharField(max_length=1000, blank=True), default=list
    )
    rule_langs = ArrayField(
        models.CharField(max_length=400, blank=True), default=list
    )
    rule_relbranch = models.CharField(max_length=500)
    created_on = models.DateTimeField()
    rule_status = models.BooleanField(default=True)
    rule_visibility_public = models.BooleanField(default=False)
    created_by = models.EmailField(null=True)

    class Meta:
        db_table = TABLE_PREFIX + 'graphrules'


class CacheAPI(models.Model):
    """Cache API Model"""
    cache_api_id = models.AutoField(primary_key=True)
    base_url = models.URLField(max_length=800)
    resource = models.CharField(max_length=200)
    request_args = ArrayField(
        models.CharField(max_length=400, blank=True), default=list
    )
    request_kwargs = models.CharField(max_length=1000)
    response_content = models.TextField(max_length=10000)
    response_content_json = JSONField(null=True)
    expiry = models.DateTimeField()

    class Meta:
        db_table = TABLE_PREFIX + 'cacheapi'


class Reports(models.Model):
    """Reports Model"""
    reports_id = models.AutoField(primary_key=True)
    report_subject = models.CharField(max_length=200, unique=True)
    report_json = JSONField(null=True)
    report_updated = models.DateTimeField(null=True)

    def __str__(self):
        return self.report_subject

    class Meta:
        db_table = TABLE_PREFIX + 'reports'
        verbose_name = "Reports"


class Visitor(models.Model):
    """Visitors Model"""
    visitor_id = models.AutoField(primary_key=True)
    visitor_ip = models.GenericIPAddressField()
    visitor_user_agent = models.CharField(max_length=500)
    visitor_accept = models.CharField(max_length=500, null=True, blank=True)
    visitor_encoding = models.CharField(max_length=500, null=True, blank=True)
    visitor_language = models.CharField(max_length=500, null=True, blank=True)
    visitor_host = models.CharField(max_length=500, null=True, blank=True)
    first_visit_time = models.DateTimeField()
    last_visit_time = models.DateTimeField()

    def save(self, *args, **kwargs):
        if not self.visitor_id:
            self.first_visit_time = timezone.now()
        self.last_visit_time = timezone.now()
        return super(Visitor, self).save(*args, **kwargs)

    def __str__(self):
        return "%s: %s" % (str(self.visitor_ip), self.visitor_user_agent)

    class Meta:
        db_table = TABLE_PREFIX + 'visitors'
        verbose_name = "Visitors"


@receiver(post_save, sender=settings.AUTH_USER_MODEL)
def create_auth_token(sender, instance=None, created=False, **kwargs):
    if created:
        Token.objects.create(user=instance)
