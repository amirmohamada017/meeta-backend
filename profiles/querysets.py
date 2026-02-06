from django.db import models


class ProfileQuerySet(models.QuerySet):
    def with_full_details(self):
        return self.select_related('user')
    
    def with_public_details(self):
        return self
    
    def with_basic_details(self):
        return self.select_related('user')
