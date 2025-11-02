import requests
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from django.core.cache import cache
from .models import UserLocation
from .serializers import UserLocationSerializer

# Comprehensive African Locations Data
AFRICAN_LOCATIONS = [
    # Ghana - All Regions and Major Towns
    {"name": "Accra", "country": "Ghana", "region": "Greater Accra", "lat": 5.6037, "lon": -0.1870, "local_name": "Accra"},
    {"name": "Kumasi", "country": "Ghana", "region": "Ashanti", "lat": 6.7000, "lon": -1.6167, "local_name": "Kumasi"},
    {"name": "Tamale", "country": "Ghana", "region": "Northern", "lat": 9.4000, "lon": -0.8500, "local_name": "Tamale"},
    {"name": "Takoradi", "country": "Ghana", "region": "Western", "lat": 4.9010, "lon": -1.7833, "local_name": "Takoradi"},
    {"name": "Cape Coast", "country": "Ghana", "region": "Central", "lat": 5.1000, "lon": -1.2500, "local_name": "Cape Coast"},
    {"name": "Sunyani", "country": "Ghana", "region": "Bono", "lat": 7.3333, "lon": -2.3333, "local_name": "Sunyani"},
    {"name": "Ho", "country": "Ghana", "region": "Volta", "lat": 6.6000, "lon": 0.4667, "local_name": "Ho"},
    {"name": "Wa", "country": "Ghana", "region": "Upper West", "lat": 10.0600, "lon": -2.5000, "local_name": "Wa"},
    {"name": "Bolgatanga", "country": "Ghana", "region": "Upper East", "lat": 10.7850, "lon": -0.8514, "local_name": "Bolgatanga"},
    {"name": "Koforidua", "country": "Ghana", "region": "Eastern", "lat": 6.0833, "lon": -0.2500, "local_name": "Koforidua"},
    
    # Nigeria - Major Cities
    {"name": "Lagos", "country": "Nigeria", "region": "Lagos", "lat": 6.5244, "lon": 3.3792, "local_name": "Lagos"},
    {"name": "Abuja", "country": "Nigeria", "region": "Federal Capital Territory", "lat": 9.0579, "lon": 7.4951, "local_name": "Abuja"},
    {"name": "Kano", "country": "Nigeria", "region": "Kano", "lat": 12.0022, "lon": 8.5927, "local_name": "Kano"},
    {"name": "Ibadan", "country": "Nigeria", "region": "Oyo", "lat": 7.3776, "lon": 3.9470, "local_name": "Ibadan"},
    {"name": "Port Harcourt", "country": "Nigeria", "region": "Rivers", "lat": 4.8156, "lon": 7.0498, "local_name": "Port Harcourt"},
    
    # Kenya
    {"name": "Nairobi", "country": "Kenya", "region": "Nairobi", "lat": -1.2864, "lon": 36.8172, "local_name": "Nairobi"},
    {"name": "Mombasa", "country": "Kenya", "region": "Mombasa", "lat": -4.0435, "lon": 39.6682, "local_name": "Mombasa"},
    {"name": "Kisumu", "country": "Kenya", "region": "Kisumu", "lat": -0.1022, "lon": 34.7617, "local_name": "Kisumu"},
    {"name": "Nakuru", "country": "Kenya", "region": "Nakuru", "lat": -0.3031, "lon": 36.0800, "local_name": "Nakuru"},
    
    # South Africa
    {"name": "Johannesburg", "country": "South Africa", "region": "Gauteng", "lat": -26.2041, "lon": 28.0473, "local_name": "Johannesburg"},
    {"name": "Cape Town", "country": "South Africa", "region": "Western Cape", "lat": -33.9249, "lon": 18.4241, "local_name": "Cape Town"},
    {"name": "Durban", "country": "South Africa", "region": "KwaZulu-Natal", "lat": -29.8587, "lon": 31.0218, "local_name": "Durban"},
    {"name": "Pretoria", "country": "South Africa", "region": "Gauteng", "lat": -25.7479, "lon": 28.2293, "local_name": "Pretoria"},
    
    # Tanzania
    {"name": "Dar es Salaam", "country": "Tanzania", "region": "Dar es Salaam", "lat": -6.7924, "lon": 39.2083, "local_name": "Dar es Salaam"},
    {"name": "Dodoma", "country": "Tanzania", "region": "Dodoma", "lat": -6.1630, "lon": 35.7516, "local_name": "Dodoma"},
    {"name": "Arusha", "country": "Tanzania", "region": "Arusha", "lat": -3.3869, "lon": 36.6830, "local_name": "Arusha"},
    {"name": "Mwanza", "country": "Tanzania", "region": "Mwanza", "lat": -2.5164, "lon": 32.9176, "local_name": "Mwanza"},
    
    # Uganda
    {"name": "Kampala", "country": "Uganda", "region": "Central", "lat": 0.3476, "lon": 32.5825, "local_name": "Kampala"},
    {"name": "Entebbe", "country": "Uganda", "region": "Central", "lat": 0.0500, "lon": 32.4600, "local_name": "Entebbe"},
    {"name": "Jinja", "country": "Uganda", "region": "Eastern", "lat": 0.4244, "lon": 33.2042, "local_name": "Jinja"},
    
    # Ethiopia
    {"name": "Addis Ababa", "country": "Ethiopia", "region": "Addis Ababa", "lat": 9.0320, "lon": 38.7469, "local_name": "Addis Ababa"},
    {"name": "Dire Dawa", "country": "Ethiopia", "region": "Dire Dawa", "lat": 9.5892, "lon": 41.8664, "local_name": "Dire Dawa"},
    
    # Rwanda
    {"name": "Kigali", "country": "Rwanda", "region": "Kigali", "lat": -1.9441, "lon": 30.0619, "local_name": "Kigali"},
    
    # Senegal
    {"name": "Dakar", "country": "Senegal", "region": "Dakar", "lat": 14.7167, "lon": -17.4677, "local_name": "Dakar"},
    
    # Ivory Coast
    {"name": "Abidjan", "country": "Ivory Coast", "region": "Abidjan", "lat": 5.3600, "lon": -4.0083, "local_name": "Abidjan"},
    
    # Cameroon
    {"name": "Yaoundé", "country": "Cameroon", "region": "Centre", "lat": 3.8480, "lon": 11.5021, "local_name": "Yaoundé"},
    {"name": "Douala", "country": "Cameroon", "region": "Littoral", "lat": 4.0511, "lon": 9.7679, "local_name": "Douala"},
]

# Enhanced Language Translations for Farming Advice
LANGUAGE_TRANSLATIONS = {
    'en': {  # English
        'rain_alert': 'Rain alert! High chance of rain today',
        'heavy_rain_alert': 'Heavy rain warning! Very high chance of heavy rain',
        'sunny_alert': 'Sunny weather today. Good for farming activities',
        'hot_sunny_alert': 'Hot and sunny today. High temperatures expected',
        'storm_warning': 'Storm warning! Dangerous weather conditions',
        'general_weather': 'Weather update for today',
        'temperature_is': 'Temperature is',
        'recommended': 'Recommended activities',
        'avoid': 'Avoid these activities',
        'good_for_crops': 'Good for crops',
        'avoid_spraying': 'Avoid spraying chemicals',
        'good_planting': 'Good for planting',
        'good_harvest': 'Good for harvesting',
        'prepare_drainage': 'Prepare drainage systems',
        'harvest_ripe': 'Harvest ripe crops',
        'natural_irrigation': 'Good for natural irrigation',
        'field_preparation': 'Field preparation',
        'drying_crops': 'Drying crops',
        'secure_farm': 'Secure farm structures',
        'protect_animals': 'Protect animals',
        'water_plants': 'Water plants regularly',
        'chemical_applications': 'Chemical applications',
        'field_work_rain': 'Field work during rain',
        'planting_new': 'Planting new crops',
        'working_peak_heat': 'Working during peak heat',
        'crops_exposed': 'Leaving crops exposed',
        'all_outdoor': 'All outdoor activities',
        'working_fields': 'Working in fields',
    },
    'tw': {  # Twi (Ghana)
        'rain_alert': 'Ensuo B3 tumi atc',
        'heavy_rain_alert': 'Nsuo B3 tumi atc k3se3 paa ',
        'sunny_alert': '3wia b3bc wob3 tumi ay3 adwuma ',
        'hot_sunny_alert': 'Awɔ wiase anɔpa. Mframa be hye kɛse',
        'storm_warning': 'Mframa duru! Mframa bone be ba',
        'general_weather': 'Wim tebea ho nsɛm',
        'temperature_is': 'Mframa hyeɛ yɛ',
        'recommended': 'Deɛ ɛsɛ sɛ woyɛ',
        'avoid': 'Mfa nhwɛ',
        'good_for_crops': 'Ɛyɛ ma aduaba',
        'avoid_spraying': '3nmc aduro 3n3',
        'good_planting': 'Ɛyɛ ma s3 wob3 dua 3nc bae',
        'good_harvest': 'Ɛyɛ ma s3 wob3 twa wo nncbae',
        'prepare_drainage': 'Siesie nsuo a ɛretu',
        'harvest_ripe': 'Yi mmerɛ a ɛso',
        'natural_irrigation': 'Ɛyɛ ma nsuo a wɔde ma mmerɛ',
        'field_preparation': 'Siesie fam',
        'drying_crops': 'Mmerɛ a wɔayɛ no nwini',
        'secure_farm': 'Dan adan no yie',
        'protect_animals': 'Hwɛ mmoa so',
        'water_plants': 'Ma nsuo mmerɛ so daa',
        'chemical_applications': 'Nnoɔma a ɛyɛ den',
        'field_work_rain': 'Adwuma wɔ fam bere a nsuo reto',
        'planting_new': 'Duaduan foforo',
        'working_peak_heat': 'Adwuma bere a ɛhyɛ kɛse',
        'crops_exposed': 'Mmerɛ a wɔagyae wɔ hɔ',
        'all_outdoor': 'Adwuma a wɔyɛ wɔ abonten nyinaa',
        'working_fields': 'Adwuma wɔ fam',
    },
    'fr': {  # French
        'rain_alert': 'Alerte pluie! Forte probabilité de pluie aujourd\'hui',
        'heavy_rain_alert': 'Alerte pluie torrentielle! Très forte probabilité de pluie',
        'sunny_alert': 'Temps ensoleillé aujourd\'hui. Bon pour les activités agricoles',
        'hot_sunny_alert': 'Chaud et ensoleillé aujourd\'hui. Températures élevées attendues',
        'storm_warning': 'Alerte tempête! Conditions météorologiques dangereuses',
        'general_weather': 'Mise à jour météo pour aujourd\'hui',
        'temperature_is': 'La température est de',
        'recommended': 'Activités recommandées',
        'avoid': 'Évitez ces activités',
        'good_for_crops': 'Bon pour les cultures',
        'avoid_spraying': 'Évitez de pulvériser des produits chimiques',
        'good_planting': 'Bon pour la plantation',
        'good_harvest': 'Bon pour la récolte',
        'prepare_drainage': 'Préparez les systèmes de drainage',
        'harvest_ripe': 'Récoltez les cultures mûres',
        'natural_irrigation': 'Bon pour l\'irrigation naturelle',
        'field_preparation': 'Préparation du terrain',
        'drying_crops': 'Séchage des cultures',
        'secure_farm': 'Sécurisez les structures agricoles',
        'protect_animals': 'Protégez les animaux',
        'water_plants': 'Arrosez les plantes régulièrement',
        'chemical_applications': 'Applications chimiques',
        'field_work_rain': 'Travail des champs pendant la pluie',
        'planting_new': 'Planter de nouvelles cultures',
        'working_peak_heat': 'Travailler pendant les heures chaudes',
        'crops_exposed': 'Laisser les cultures exposées',
        'all_outdoor': 'Toutes les activités extérieures',
        'working_fields': 'Travailler dans les champs',
    },
    'sw': {  # Swahili
        'rain_alert': 'Taarifa ya mvua! Uwezekano mkubwa wa mvua leo',
        'heavy_rain_alert': 'Onyo la mvua kubwa! Uwezekano mkubwa sana wa mvua kubwa',
        'sunny_alert': 'Hali ya hewa ya jua leo. Nzuri kwa shughuli za kilimo',
        'hot_sunny_alert': 'Joto na jua leo. Joto kubwa linatarajiwa',
        'storm_warning': 'Onyo la dhoruba! Hali mbaya ya hewa',
        'general_weather': 'Habari ya hali ya hewa leo',
        'temperature_is': 'Joto ni',
        'recommended': 'Shughuli zilizopendekezwa',
        'avoid': 'Epuka shughuli hizi',
        'good_for_crops': 'Nzuri kwa mazao',
        'avoid_spraying': 'Epuka kufyeka dawa',
        'good_planting': 'Nzuri kwa kupanda',
        'good_harvest': 'Nzuri kwa kuvuna',
        'prepare_drainage': 'Andaa mifumo ya maji',
        'harvest_ripe': 'Vuna mazao yaliyokomaa',
        'natural_irrigation': 'Nzuri kwa umwagiliaji wa asili',
        'field_preparation': 'Maandalizi ya shamba',
        'drying_crops': 'Kukausha mazao',
        'secure_farm': 'Linda majengo ya shamba',
        'protect_animals': 'Linda wanyama',
        'water_plants': 'Umwagilia mimea mara kwa mara',
        'chemical_applications': 'Matumizi ya kemikali',
        'field_work_rain': 'Kazi shambani wakati wa mvua',
        'planting_new': 'Kupanda mazao mapya',
        'working_peak_heat': 'Kufanya kazi wakati wa joto kali',
        'crops_exposed': 'Kuacha mazao wazi',
        'all_outdoor': 'Shughuli zote za nje',
        'working_fields': 'Kufanya kazi shambani',
    },
    'yo': {  # Yoruba
        'rain_alert': 'Ikilo ojo! Ojo maa ro pupo lonii',
        'heavy_rain_alert': 'Ikilo ojo riru! Ojo maa ro gan-an lonii',
        'sunny_alert': 'Oju oorun lonii. O dara fun ise oko',
        'hot_sunny_alert': 'Ooru ati oorun lonii. Ooru pupo ni a nreti',
        'storm_warning': 'Ikilo iji! Oju ojo lewu',
        'general_weather': 'Alaye oju ojo fun oni',
        'temperature_is': 'Ooru wa ni',
        'recommended': 'Awon ise ti a gba niyanju',
        'avoid': 'Yago fun awon ise wonyi',
        'good_for_crops': 'O dara fun ohun ogbin',
        'avoid_spraying': 'Yago fun gbigbe kemikali',
        'good_planting': 'O dara fun gbigbin',
        'good_harvest': 'O dara fun ikore',
        'prepare_drainage': 'Pese eto omi',
        'harvest_ripe': 'Kore ohun ogbin ti o pon',
        'natural_irrigation': 'O dara fun omi isan',
        'field_preparation': 'Isopapo papa',
        'drying_crops': 'Gbigbe ohun ogbin',
        'secure_farm': 'Dabobo ile oko',
        'protect_animals': 'Dabobo eran',
        'water_plants': 'Fun omi si ohun ogbin nigbakugba',
        'chemical_applications': 'Lilo kemikali',
        'field_work_rain': 'Sise papa nigba ojo',
        'planting_new': 'Gbigbin ohun ogbin titun',
        'working_peak_heat': 'Sise nigba ooru gbigbona',
        'crops_exposed': 'Fifo ohun ogbin silẹ',
        'all_outdoor': 'Gbogbo ise ita',
        'working_fields': 'Sise ninu papa',
    }
}

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_african_locations(request):
    """Get all African locations"""
    country = request.GET.get('country', '')
    
    if country:
        locations = [loc for loc in AFRICAN_LOCATIONS if loc['country'].lower() == country.lower()]
    else:
        locations = AFRICAN_LOCATIONS
        
    return Response(locations)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_african_countries(request):
    """Get list of all African countries available"""
    countries = sorted(list(set(loc['country'] for loc in AFRICAN_LOCATIONS)))
    return Response(countries)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def save_user_location(request):
    """Save user's selected location and language"""
    serializer = UserLocationSerializer(data=request.data)
    if serializer.is_valid():
        user_location, created = UserLocation.objects.update_or_create(
            user=request.user,
            defaults=serializer.validated_data
        )
        return Response({
            'message': 'Location saved successfully',
            'location': UserLocationSerializer(user_location).data
        })
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_user_location(request):
    """Get user's saved location"""
    try:
        user_location = UserLocation.objects.get(user=request.user)
        return Response(UserLocationSerializer(user_location).data)
    except UserLocation.DoesNotExist:
        return Response({'detail': 'No location saved'})

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_weather(request):
    """Get weather for any African location with farming advice"""
    city = request.GET.get('city', 'Accra')
    country = request.GET.get('country', 'Ghana')
    language = request.GET.get('language', 'en')
    
    # Find the location
    location = next((loc for loc in AFRICAN_LOCATIONS 
                    if loc['name'].lower() == city.lower() 
                    and loc['country'].lower() == country.lower()), None)
    
    if not location:
        return Response({'error': 'Location not found'}, status=400)
    
    # Check cache first
    cache_key = f"weather_{city}_{country}"
    cached_weather = cache.get(cache_key)
    
    if cached_weather:
        return Response(cached_weather)
    
    try:
        # Use Open-Meteo API (FREE, NO LIMITS)
        url = f"https://api.open-meteo.com/v1/forecast?latitude={location['lat']}&longitude={location['lon']}&current_weather=true&daily=weathercode,temperature_2m_max,temperature_2m_min,precipitation_probability_max&timezone=auto"
        
        response = requests.get(url, timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            
            # Get farming advice based on weather
            weather_advice = _get_farming_advice(data, language)
            
            # Generate voice message based on weather conditions
            voice_message = _generate_voice_message(data, weather_advice, language)
            
            # Format weather data
            weather_data = {
                'location': {
                    'name': location['name'],
                    'country': location['country'],
                    'region': location['region'],
                    'local_name': location.get('local_name', location['name'])
                },
                'current': {
                    'temperature': round(data['current_weather']['temperature']),
                    'weather_type': _get_weather_type(data['current_weather']['weathercode']),
                    'description': _get_weather_description(data['current_weather']['weathercode'], language),
                    'wind_speed': data['current_weather']['windspeed'],
                    'is_day': data['current_weather']['is_day']
                },
                'today': {
                    'max_temp': round(data['daily']['temperature_2m_max'][0]),
                    'min_temp': round(data['daily']['temperature_2m_min'][0]),
                    'rain_chance': data['daily']['precipitation_probability_max'][0],
                    'icon': _get_weather_icon(data['current_weather']['weathercode'])
                },
                'forecast': _get_weekly_forecast(data),
                'farming_advice': weather_advice,
                'voice_message': voice_message,
                'alerts': _get_weather_alerts(data, language)
            }
            
            # Cache for 30 minutes
            cache.set(cache_key, weather_data, 1800)
            
            return Response(weather_data)
        else:
            return Response({'error': 'Weather service busy'}, status=503)
            
    except requests.Timeout:
        return Response({'error': 'Weather service timeout'}, status=504)
    except Exception as e:
        return Response({'error': 'Failed to get weather data'}, status=500)

def _get_weather_type(weather_code):
    """Convert weather code to simple type"""
    if weather_code in [0, 1]:
        return 'sunny'
    elif weather_code in [2, 3]:
        return 'cloudy'
    elif weather_code >= 51 and weather_code <= 67:
        return 'rain'
    elif weather_code >= 80 and weather_code <= 82:
        return 'heavy_rain'
    elif weather_code >= 95:
        return 'storm'
    else:
        return 'partly_cloudy'

def _get_weather_description(weather_code, language='en'):
    """Get weather description in selected language"""
    descriptions = {
        'sunny': {'en': 'Sunny', 'tw': 'Awia b3bc', 'fr': 'Ensoleillé', 'sw': 'Jua', 'yo': 'Oju oorun'},
        'cloudy': {'en': 'Cloudy', 'tw': 'Ewiem b3 y3 kusuu', 'fr': 'Nuageux', 'sw': 'Wingu', 'yo': 'Oju awọ'},
        'rain': {'en': 'Rainy', 'tw': 'Nsuo betumi atc', 'fr': 'Pluvieux', 'sw': 'Mvua', 'yo': 'Ojo nro'},
        'heavy_rain': {'en': 'Heavy Rain', 'tw': 'Nsuo den den b3tc', 'fr': 'Forte pluie', 'sw': 'Mvua kubwa', 'yo': 'Ojo riru'},
        'storm': {'en': 'Stormy', 'tw': 'Mframa duru', 'fr': 'Orageux', 'sw': 'Dhoruba', 'yo': 'Iji'},
    }
    
    weather_type = _get_weather_type(weather_code)
    return descriptions.get(weather_type, {}).get(language, descriptions[weather_type]['en'])

def _get_weather_icon(weather_code):
    """Get appropriate weather icon"""
    weather_type = _get_weather_type(weather_code)
    icons = {
        'sunny': '☀️',
        'cloudy': '⛅',
        'rain': '🌧️',
        'heavy_rain': '⛈️',
        'storm': '⚡',
    }
    return icons.get(weather_type, '⛅')

def _get_farming_advice(weather_data, language='en'):
    """Generate farming advice based on weather"""
    weather_code = weather_data['current_weather']['weathercode']
    rain_chance = weather_data['daily']['precipitation_probability_max'][0]
    temperature = weather_data['current_weather']['temperature']
    
    advice = {
        'do': [],
        'avoid': [],
        'warning': []
    }
    
    # Get translations
    translations = LANGUAGE_TRANSLATIONS.get(language, LANGUAGE_TRANSLATIONS['en'])
    
    # High rain conditions
    if rain_chance > 70:
        advice['do'].extend([
            translations['good_for_crops'],
            translations['prepare_drainage'],
            translations['harvest_ripe']
        ])
        advice['avoid'].extend([
            translations['avoid_spraying'],
            translations['field_work_rain'],
            translations['planting_new']
        ])
        advice['warning'].append(translations['heavy_rain_alert'])
    
    # Moderate rain
    elif rain_chance > 40:
        advice['do'].extend([
            translations['good_for_crops'],
            translations['natural_irrigation']
        ])
        advice['avoid'].extend([
            translations['avoid_spraying'],
            translations['chemical_applications']
        ])
        advice['warning'].append(translations['rain_alert'])
    
    # Sunny and hot
    elif weather_code in [0, 1] and temperature > 30:
        advice['do'].extend([
            translations['good_planting'],
            translations['good_harvest'],
            translations['drying_crops'],
            translations['field_preparation']
        ])
        advice['avoid'].extend([
            translations['working_peak_heat'],
            translations['crops_exposed']
        ])
        advice['warning'].append(translations['hot_sunny_alert'])
    
    # Normal sunny
    elif weather_code in [0, 1]:
        advice['do'].extend([
            translations['good_planting'],
            translations['good_harvest'],
            'All field work',
            'Spraying and fertilizing'
        ])
        advice['warning'].append(translations['sunny_alert'])
    
    # Storm conditions
    elif weather_code >= 95:
        advice['do'].extend([
            translations['secure_farm'],
            translations['harvest_ripe'],
            translations['protect_animals']
        ])
        advice['avoid'].extend([
            translations['all_outdoor'],
            translations['working_fields']
        ])
        advice['warning'].append(translations['storm_warning'])
    
    # Cloudy conditions
    elif weather_code in [2, 3]:
        advice['do'].extend([
            translations['good_planting'],
            'Light field work',
            'Crop maintenance'
        ])
        advice['warning'].append(translations['general_weather'])
    
    return advice

def _generate_voice_message(weather_data, advice, language='en'):
    """Generate detailed voice message based on weather conditions"""
    weather_code = weather_data['current_weather']['weathercode']
    temperature = round(weather_data['current_weather']['temperature'])
    rain_chance = weather_data['daily']['precipitation_probability_max'][0]
    
    # Get translations
    translations = LANGUAGE_TRANSLATIONS.get(language, LANGUAGE_TRANSLATIONS['en'])
    
    # Base message based on weather type
    weather_type = _get_weather_type(weather_code)
    
    if weather_type == 'rain' or rain_chance > 60:
        if rain_chance > 80:
            message = translations['heavy_rain_alert']
        else:
            message = translations['rain_alert']
    elif weather_type == 'sunny' and temperature > 30:
        message = translations['hot_sunny_alert']
    elif weather_type == 'sunny':
        message = translations['sunny_alert']
    elif weather_type == 'storm':
        message = translations['storm_warning']
    else:
        message = translations['general_weather']
    
    # Add temperature information
    message += f". {translations['temperature_is']} {temperature} degrees. "
    
    # Add farming advice
    if advice['do']:
        message += f"{translations['recommended']}: {', '.join(advice['do'][:2])}. "
    
    if advice['avoid']:
        message += f"{translations['avoid']}: {', '.join(advice['avoid'][:2])}."
    
    return message

def _get_weather_alerts(weather_data, language='en'):
    """Generate weather alerts"""
    weather_code = weather_data['current_weather']['weathercode']
    rain_chance = weather_data['daily']['precipitation_probability_max'][0]
    
    alerts = []
    translations = LANGUAGE_TRANSLATIONS.get(language, LANGUAGE_TRANSLATIONS['en'])
    
    if rain_chance > 80:
        alerts.append(translations['heavy_rain_alert'])
    elif rain_chance > 60:
        alerts.append(translations['rain_alert'])
    elif weather_code >= 95:
        alerts.append(translations['storm_warning'])
    
    return alerts

def _get_weekly_forecast(weather_data):
    """Get 7-day forecast"""
    forecast = []
    
    for i in range(7):
        forecast.append({
            'day': i,
            'max_temp': round(weather_data['daily']['temperature_2m_max'][i]),
            'min_temp': round(weather_data['daily']['temperature_2m_min'][i]),
            'rain_chance': weather_data['daily']['precipitation_probability_max'][i],
            'icon': _get_weather_icon(weather_data['daily']['weathercode'][i])
        })
    
    return forecast