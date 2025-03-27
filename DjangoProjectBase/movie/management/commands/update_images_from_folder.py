import os
from django.core.management.base import BaseCommand
from movie.models import Movie
 
class Command(BaseCommand):
    help = "Update movie images in the database from a media folder"
 
    def handle(self, *args, **options):
        media_folder = 'media/movie/images/'
 
        if not os.path.exists(media_folder):
            self.stderr.write(f"Media folder '{media_folder}' not found.")
            return
        updated_count = 0
 
        # Iterate over all files in the media folder
        for filename in os.listdir(media_folder):
            if filename.startswith("m_") and filename.endswith((".jpg", ".png", ".jpeg")):
                movie_title = filename[2:].rsplit('.', 1)[0]  # Remove "m_" prefix and file extension
 
                try:
                    movie = Movie.objects.get(title=movie_title)
                    # Store only the relative path from MEDIA_ROOT
                    movie.image = f"movie/images/{filename}"  # Omit 'media/' prefix
                    movie.save()
                    updated_count += 1
                    self.stdout.write(self.style.SUCCESS(f"Updated image for movie: {movie_title}"))
                except Movie.DoesNotExist:
                    self.stderr.write(f"Movie with title '{movie_title}' not found in the database.")
                except Exception as e:
                    self.stderr.write(f"Error updating movie '{movie_title}': {str(e)}")
 
        self.stdout.write(self.style.SUCCESS(f"Successfully updated {updated_count} movie images."))