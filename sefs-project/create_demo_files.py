"""Create demo files for SEFS hackathon"""

from pathlib import Path

ROOT = Path("sefs_root")
ROOT.mkdir(exist_ok=True)

# AI/ML papers
ai_content = [
    """Deep Learning and Neural Networks

This paper explores the fundamentals of deep learning architectures including
convolutional neural networks, recurrent neural networks, and transformers.
We discuss backpropagation, gradient descent, and modern optimization techniques.
Applications include computer vision, natural language processing, and speech recognition.""",

    """Transformer Architecture and Attention Mechanisms

The transformer model revolutionized natural language processing with its
attention mechanism. This allows the model to focus on relevant parts of
the input sequence. BERT, GPT, and similar models are based on this architecture.
Applications include machine translation, text generation, and question answering.""",

    """Reinforcement Learning Fundamentals

Reinforcement learning teaches agents to make decisions through trial and error.
Key concepts include rewards, policies, value functions, and Q-learning.
Deep Q-Networks combine neural networks with reinforcement learning.
Applications include game playing, robotics, and autonomous systems."""
]

for i, content in enumerate(ai_content, 1):
    (ROOT / f"ai_paper_{i}.txt").write_text(content)

# Cooking recipes
cooking_content = [
    """Classic Chocolate Cake Recipe

Ingredients: flour, sugar, cocoa powder, eggs, butter, milk, vanilla extract

Instructions:
1. Preheat oven to 350°F
2. Mix dry ingredients: flour, sugar, cocoa powder
3. Beat eggs and add butter, milk, vanilla
4. Combine wet and dry ingredients
5. Pour into greased pan and bake for 30 minutes

Serves 8-10 people. Perfect for birthdays and celebrations.""",

    """Authentic Italian Pasta Carbonara

Ingredients: spaghetti, eggs, parmesan cheese, pancetta, black pepper

Instructions:
1. Cook spaghetti according to package directions
2. Fry pancetta until crispy
3. Beat eggs with grated parmesan
4. Toss hot pasta with egg mixture off heat
5. Add pancetta and lots of black pepper

Traditional Roman recipe. No cream!""",

    """Homemade Pizza Dough Recipe

Ingredients: flour, yeast, water, olive oil, salt, sugar

Instructions:
1. Mix yeast with warm water and sugar
2. Add flour, salt, and olive oil
3. Knead dough for 10 minutes
4. Let rise for 1 hour
5. Shape and add toppings
6. Bake at 450°F for 12-15 minutes

Makes 2 large pizzas. Perfect for pizza night!"""
]

for i, content in enumerate(cooking_content, 1):
    (ROOT / f"recipe_{i}.txt").write_text(content)

# Travel guides
travel_content = [
    """Paris Travel Guide

Must-see attractions:
- Eiffel Tower: Iconic landmark, best at sunset
- Louvre Museum: Home to Mona Lisa and thousands of artworks
- Notre-Dame Cathedral: Gothic architecture masterpiece
- Champs-Élysées: Famous shopping avenue
- Montmartre: Artistic neighborhood with Sacré-Cœur

Best time to visit: Spring (April-June) or Fall (September-October)
Transportation: Metro is efficient and covers entire city
Food: Try croissants, escargot, and coq au vin""",

    """Tokyo Travel Guide

Must-see attractions:
- Senso-ji Temple: Ancient Buddhist temple in Asakusa
- Shibuya Crossing: World's busiest pedestrian crossing
- Tokyo Skytree: Tallest structure in Japan
- Tsukiji Fish Market: Fresh seafood and sushi
- Imperial Palace: Home of Japanese Emperor

Best time to visit: Spring (cherry blossoms) or Fall
Transportation: JR Pass for trains, very punctual
Food: Ramen, sushi, tempura, and yakitori""",

    """Barcelona Travel Guide

Must-see attractions:
- Sagrada Familia: Gaudí's unfinished masterpiece
- Park Güell: Colorful mosaic park by Gaudí
- Las Ramblas: Famous tree-lined pedestrian street
- Gothic Quarter: Medieval streets and architecture
- Beach: Barceloneta beach for Mediterranean sun

Best time to visit: May-June or September-October
Transportation: Metro and buses cover the city
Food: Tapas, paella, and sangria"""
]

for i, content in enumerate(travel_content, 1):
    (ROOT / f"travel_guide_{i}.txt").write_text(content)

print("✅ Demo files created successfully!")
print(f"Created 9 files in {ROOT}/")
