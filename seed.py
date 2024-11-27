from django_seed import Seed

seeder = Seed.seeder("en_US")

from library.models import Author

seeder.add_entity(Author, 5)

inserted_pks = seeder.execute()
