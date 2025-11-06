import uuid

from django.db import models
from django.contrib.auth import get_user_model
from django.utils import timezone

from api.models import TimeStampedModel

User = get_user_model()

class Workspace(TimeStampedModel):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=200)
    owner = models.ForeignKey(User, on_delete=models.PROTECT, related_name="owned_workspaces")
    members = models.ManyToManyField(User, through="WorkspaceMembership", related_name="workspaces")
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return self.name
    

class WorkspaceMembership(models.Model):
    class Role(models.TextChoices):
        ADMIN = "admin", "Admin"
        MEMBER = "member", "Member"

    workspace = models.ForeignKey(Workspace, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    role = models.CharField(max_length=20, choices=Role.choices, default=Role.MEMBER)
    joined_at = models.DateTimeField(default=timezone.now)

    class Meta:
        unique_together = ("workspace", "user")


class Integration(TimeStampedModel):
    """
    Represents a connector type (e.g., Google Sheets, Slack).
    Not a user connection — these are available integrations.
    """
    id = models.SlugField(primary_key=True)  # e.g. "google_sheets", "slack"
    name = models.CharField(max_length=150)
    description = models.TextField(blank=True)
    config_schema = models.JSONField(default=dict)  # UI hints: fields required, types, OAuth vs API Key
    oauth_enabled = models.BooleanField(default=False)
    webhook_supported = models.BooleanField(default=False)

    def __str__(self):
        return self.name


class Connection(TimeStampedModel):
    """
    A workspace-specific connection/credential to an Integration (i.e., auth tokens).
    """
    class Status(models.TextChoices):
        ACTIVE = "active", "Active"
        DISABLED = "disabled", "Disabled"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    workspace = models.ForeignKey(Workspace, on_delete=models.CASCADE, related_name="connections")
    integration = models.ForeignKey(Integration, on_delete=models.PROTECT, related_name="connections")
    display_name = models.CharField(max_length=200)
    config = models.JSONField(default=dict)     
    secrets = models.JSONField(default=dict)        
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.ACTIVE)
    last_tested = models.DateTimeField(null=True, blank=True)

    class Meta:
        indexes = [
            models.Index(fields=["workspace", "integration"]),
        ]

    def __str__(self):
        return f"{self.display_name} ({self.integration.id})"
    

class Automation(TimeStampedModel):
    """
    A user's automation (Zap-like thingy hehe). Composed of ordered Steps.
    """
    class Status(models.TextChoices):
        DRAFT = "draft", "Draft"
        ENABLED = "enabled", "Enabled"
        DISABLED = "disabled", "Disabled"
        PAUSED = "paused", "Paused"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    workspace = models.ForeignKey(Workspace, on_delete=models.CASCADE, related_name="automations")
    name = models.CharField(max_length=255)
    owner = models.ForeignKey(User, on_delete=models.PROTECT, related_name="automations")
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.DRAFT)
    # NOTE: Should an automation have multiple trigers? 
    trigger = models.ForeignKey("Trigger", null=True, blank=True, on_delete=models.SET_NULL, related_name="+")
    settings = models.JSONField(default=dict)

    class Meta:
        indexes = [models.Index(fields=["workspace", "status"])]

    def __str__(self):
        return self.name


class Trigger(TimeStampedModel):
    """
    Defines the trigger for an Automation. Could be webhook, polling, or schedule.
    """
    class Type(models.TextChoices):
        WEBHOOK = "webhook", "Webhook"
        POLL = "poll", "Polling"
        SCHEDULE = "schedule", "Schedule"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    trigger_key = models.CharField(max_length=100)
    type = models.CharField(max_length=20, choices=Type.choices)
    config = models.JSONField(default=dict)
    integration = models.OneToOneField(Integration, on_delete=models.CASCADE)
    connection = models.ForeignKey(Connection, null=True, blank=True, on_delete=models.SET_NULL)
    automation = models.ForeignKey("Automation", on_delete=models.CASCADE, related_name="triggers")

    def __str__(self):
        return f"{self.type} trigger for {self.automation.id}"
    

class Step(TimeStampedModel):
    """
    Single step inside an Automation: either an action or condition/brancher.
    Steps are ordered by `order`.
    """
    class Kind(models.TextChoices):
        ACTION = "action", "Action"
        CONDITION = "condition", "Condition"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    automation = models.ForeignKey(Automation, on_delete=models.CASCADE, related_name="steps")
    kind = models.CharField(max_length=20, choices=Kind.choices)
    order = models.PositiveIntegerField(db_index=True)
    integration = models.ForeignKey(Integration, null=True, blank=True, on_delete=models.SET_NULL)
    connection = models.ForeignKey(Connection, null=True, blank=True, on_delete=models.SET_NULL)
    # action_name identifies the specific action within integration e.g. "create_row"
    action_name = models.CharField(max_length=150, blank=True)
    # mapping & condition payload — templates or expressions that will be resolved at runtime
    config = models.JSONField(default=dict)

    class Meta:
        unique_together = ("automation", "order")
        ordering = ["order"]


class Execution(TimeStampedModel):
    """
    Represents a single run of an Automation triggered by an event.
    """
    class Status(models.TextChoices):
        PENDING = "pending", "Pending"
        RUNNING = "running", "Running"
        SUCCESS = "success", "Success"
        FAILED = "failed", "Failed"
        CANCELLED = "cancelled", "Cancelled"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    automation = models.ForeignKey(Automation, on_delete=models.CASCADE, related_name="executions")
    trigger_event = models.JSONField(default=dict)  # raw event/payload that started the execution
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.PENDING, db_index=True)
    started_at = models.DateTimeField(null=True, blank=True)
    finished_at = models.DateTimeField(null=True, blank=True)
    attempt = models.PositiveIntegerField(default=0)  # for retries

    # meta for metrics/observability (duration, cost)
    meta = models.JSONField(default=dict)

    class Meta:
        indexes = [
            models.Index(fields=["automation", "status"]),
            models.Index(fields=["created_at"]),
        ]


class Task(TimeStampedModel):
    """
    A Task is a single step execution within an Execution.
    """
    class Status(models.TextChoices):
        QUEUED = "queued", "Queued"
        RUNNING = "running", "Running"
        SUCCESS = "success", "Success"
        FAILED = "failed", "Failed"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    execution = models.ForeignKey(Execution, on_delete=models.CASCADE, related_name="tasks")
    step = models.ForeignKey(Step, null=True, blank=True, on_delete=models.SET_NULL)
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.QUEUED, db_index=True)
    # input/output snapshots (be mindful of size)
    input_payload = models.JSONField(default=dict)
    output_payload = models.JSONField(null=True, blank=True)
    error = models.TextField(null=True, blank=True)
    started_at = models.DateTimeField(null=True, blank=True)
    finished_at = models.DateTimeField(null=True, blank=True)
    attempt = models.PositiveIntegerField(default=0)

    class Meta:
        indexes = [models.Index(fields=["status", "created_at"])]


class RetryPolicy(models.Model):
    """
    Define retry/backoff behavior which can be referenced by Automations/Steps.
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=100)
    config = models.JSONField(default=dict)  # e.g. {"max_attempts": 3, "backoff": "exponential", "initial_delay": 5}
    workspace = models.ForeignKey(Workspace, on_delete=models.CASCADE, related_name="retry_policies")

    class Meta:
        unique_together = ("workspace", "name")


class WebhookEvent(TimeStampedModel):
    """
    Stores incoming webhook events for webhooks that serve as triggers.
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    trigger = models.ForeignKey(Trigger, on_delete=models.CASCADE, related_name="webhook_events")
    raw_payload = models.JSONField(default=dict)
    headers = models.JSONField(default=dict)
    processed = models.BooleanField(default=False, db_index=True)

    class Meta:
        indexes = [models.Index(fields=["processed", "created_at"])]