django-audimatic
===

Easy audit trails.

Installation
---

```shell
pip install django-audimatic

# or

pipenv install django-audimatic

# or

# install with your manager of choice
```

Usage
---

1. Add to INSTALLED_APPS

    ```python

    INSTALLED_APPS = [
        ...,
        "django_audimatic",
        ...
    ]
    ```

2. Create audit trail tables and subclass AuditTrigger

    ```python
    from django.contrib.auth.models import AbstractUser
    from django_audimatic.models import AuditTrail, AuditTrigger


    class UserAuditTrail(AuditTrail):
        pass


    class CustomUser(AbstractUser, AuditTrigger):
        class Meta(AuditTrigger.Meta):
            audit_table = UserAuditTrail
    ```

3. Register AdminModels
    ```python
    from django.contrib import admin
    from django.contrib.auth.admin import UserAdmin

    from django_audimatic.admin import DiffInline
    from testapp.models import CustomUser, UserAuditTrail


    class CustomUserAuditTrail(DiffInline):
        model = CustomUser.get_audit_table()


    class CustomUserAdmin(UserAdmin):
        inlines = (CustomUserAuditTrail,)


    admin.site.register(UserAuditTrail, admin.ModelAdmin)
    admin.site.register(CustomUser, CustomUserAdmin)

    ```

4. Add HStoreExtension
   ```python
   from django.contrib.postgres.operations import HStoreExtension

   ...
       operations = [
           HStoreExtension(),
       ]
   ...
   ```

Other
---

This project uses django-pgtrigger and django-nonrelated-inlines.

Currently, (as of Django 4.2.4) there is logic that registers these automatically, this might break in future version of Django.

There is functionality to disable migration support in pgtrigger, however that is not recommended or tested.

Inlines will always be registered as well, this is for simplicity, but maybe we add some options in the future.

License
---

Copyright 2023 Bill Schumacher

Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the "Software"), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
