from django.core.management.base import BaseCommand

from properties.models import Property


class Command(BaseCommand):
    help = "Seed sample property data for the telephony demo."

    def handle(self, *args, **options):
        property_obj, created = Property.objects.update_or_create(
            id=1,
            defaults={
                "title": "2BHK Flat",
                "location": "Wakad, Pune",
                "price": "9500000.00",
                "carpet_area": 750,
                "bedrooms": 2,
                "amenities": ["parking", "gym", "security", "clubhouse"],
                "description": "A spacious 2BHK flat in Wakad, Pune close to metro, schools, and shopping.",
                "parking_available": True,
            },
        )
        state = "created" if created else "updated"
        self.stdout.write(self.style.SUCCESS(f"Sample property {state}: {property_obj}"))
