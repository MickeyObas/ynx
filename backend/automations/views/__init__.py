from .workspace import WorkspaceViewSet
from .automations import AutomationViewSet
from .connections import ConnectionViewset
from .integrations import connection_test, integration_list, integration_detail, trigger_list
from .oauth_views import oauth_callback, start_oauth