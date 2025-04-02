from django.shortcuts import render
from movie.models import Movie
import numpy as np
import os
from openai import OpenAI
from dotenv import load_dotenv

def cosine_similarity(a, b):
    return np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b))

def get_embedding(text, client):
    response = client.embeddings.create(
        input=[text],
        model="text-embedding-3-small"
    )
    return np.array(response.data[0].embedding, dtype=np.float32)

def recommendation(request):
    prompt = request.GET.get('prompt')
    recommended_movie = None
    
    if prompt:
        # Get all movies
        movies = Movie.objects.all()
        
        if movies.exists():
            try:
                # Load OpenAI API key
                load_dotenv('openAI.env')
                api_key = os.environ.get('openai_apikey')
                
                if api_key:
                    client = OpenAI(api_key=api_key)
                    
                    # Generate embedding for the prompt
                    prompt_embedding = get_embedding(prompt, client)
                    
                    # Find the most similar movie based on embedding similarity
                    best_similarity = -1
                    best_movie = None
                    
                    for movie in movies:
                        # Convert the stored binary embedding back to numpy array
                        if movie.emb:
                            movie_embedding = np.frombuffer(movie.emb, dtype=np.float32)
                            
                            # Calculate similarity between prompt and movie
                            similarity = cosine_similarity(prompt_embedding, movie_embedding)
                            
                            # Update best match if this is better
                            if similarity > best_similarity:
                                best_similarity = similarity
                                best_movie = movie
                    
                    recommended_movie = best_movie
                    
                    # Fallback to first movie if no embeddings were found
                    if not recommended_movie and movies:
                        recommended_movie = movies.first()
                else:
                    # Fallback to a simple word-matching approach if API key is not available
                    prompt_words = set(word.lower() for word in prompt.split())
                    
                    # Filter movies that might match any word in the prompt
                    potential_matches = []
                    
                    for movie in movies:
                        title_words = set(word.lower() for word in movie.title.split())
                        desc_words = set(word.lower() for word in movie.description.split())
                        genre_words = set(word.lower() for word in movie.genre.split(',')) if movie.genre else set()
                        
                        # Calculate a simple relevance score based on word matches
                        title_matches = len(prompt_words.intersection(title_words))
                        desc_matches = len(prompt_words.intersection(desc_words))
                        genre_matches = len(prompt_words.intersection(genre_words))
                        
                        # Weight title matches more heavily
                        relevance_score = (title_matches * 3) + desc_matches + (genre_matches * 2)
                        
                        if relevance_score > 0:
                            potential_matches.append((movie, relevance_score))
                    
                    # Sort by relevance score
                    potential_matches.sort(key=lambda x: x[1], reverse=True)
                    
                    # Return the most relevant movie, or a random one if no matches
                    if potential_matches:
                        recommended_movie = potential_matches[0][0]
                    else:
                        # Fallback to random if no matches
                        import random
                        recommended_movie = random.choice(list(movies))
            except Exception as e:
                # If there's an error with the embedding process, fall back to a random movie
                import random
                recommended_movie = random.choice(list(movies))
    
    return render(request, 'recomendation.html', {
        'prompt': prompt,
        'movie': recommended_movie
    })