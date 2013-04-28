import factory
import faker
import datetime
import random
import os
from django.core.files import File
from faker.generators.utils import numerify
from libscampi.contrib.cms.communism import models as communism_models
from libscampi.contrib.cms.conduit import models as conduit_models
from libscampi.contrib.cms.newsengine import models as newsengine_models
from libscampi.contrib.cms.renaissance import models as renaissance_models
from django.contrib.auth.models import User
from django.contrib.sites.models import Site

TEST_MEDIA_PATH = os.path.join(os.path.dirname(__file__), 'tests', 'test_media')
TEST_PHOTO_PATH = os.path.join(TEST_MEDIA_PATH, 'test_photo.png')


class SiteFactory(factory.Factory):
    FACTORY_FOR = Site

    domain = "scampi-testing.local"
    name = "Scampi Testing"


class UserFactory(factory.Factory):
    FACTORY_FOR = User

    username = factory.Sequence(lambda n: 'User #{0}'.format(n))
    email = factory.Sequence(lambda n: 'email-{0}@example.com'.format(n))
    first_name = "John"
    last_name = "Doe"
    password = "pbkdf2_sha256$10000$for6jDqMIZQL$Db8smwQvDIzPDaxqzZw+6zvjCV+9uFwPXbyx7xfxUX8="
    is_active = True
    is_staff = True
    is_superuser = True


class ThemeFactory(factory.Factory):
    FACTORY_FOR = communism_models.Theme

    name = "Scampi Testing Theme"
    keyname = "scampi_testing"
    banner = factory.LazyAttribute(lambda a: File(open(TEST_PHOTO_PATH)))


class JavascriptFactory(factory.Factory):
    FACTORY_FOR = communism_models.Javascript

    name = factory.LazyAttribute(lambda x: " ".join(faker.lorem.words(1)))
    precedence = factory.Sequence(lambda n: n)
    theme = factory.SubFactory(ThemeFactory)
    # TODO File Factory business


class CSSFactory(factory.Factory):
    FACTORY_FOR = communism_models.StyleSheet

    name = factory.LazyAttribute(lambda x: " ".join(faker.lorem.words(1)))
    precedence = factory.Sequence(lambda n: n)
    theme = factory.SubFactory(ThemeFactory)
    # TODO File Factory business


class RealmFactory(factory.Factory):
    FACTORY_FOR = communism_models.Realm

    site = factory.SubFactory(SiteFactory)
    name = "Scampi Testing Realm"
    keyname = "scampi-testing-realm"
    display_order = factory.Sequence(lambda n: n)
    theme = factory.SubFactory(ThemeFactory)


class RealmNotificationFactory(factory.Factory):
    FACTORY_FOR = communism_models.RealmNotification

    realm = factory.SubFactory(RealmFactory)
    name = factory.LazyAttribute(lambda x: " ".join(faker.lorem.words(1)))
    display = factory.LazyAttribute(lambda x: " ".join(faker.lorem.words(5)))
    display_start = factory.LazyAttribute(lambda x: datetime.date(2013, 1, 10))
    display_end = factory.LazyAttribute(lambda x: datetime.date(2013, 1, 13))
