#from .functional import story_archive, story_archive_year, story_archive_month, story_archive_day, story_detail
from .base import Index

view_commune = Index.as_view()
primary_section = Index.as_view()