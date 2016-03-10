from django.test import TestCase
from django.core.urlresolvers import reverse
import json

class KpiListTest(TestCase):

    def test_kpi_tenant_scope_filter(self):
        """
        test kpi filters list righteousness.
        """

        kwargs = { 'kpi_scope' : 1, 'kpi_tenant' : 1}
        response = self.client.get(reverse('EEBModule:kpiList:kpi_list'),kwargs)
        self.assertEqual(response.status_code, 200)

        data = json.load(response)
