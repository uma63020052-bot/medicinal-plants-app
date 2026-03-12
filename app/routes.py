"""
API Routes
Main endpoints for medicinal plant identification
"""

from flask import Blueprint, request, jsonify, render_template
from werkzeug.utils import secure_filename
import os
import time
import json
import urllib.request
import urllib.error
from datetime import datetime

from app.model_loader import get_model_loader

main_bp = Blueprint('main', __name__)

ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg'}

# ─── Hardcoded fallback plant data for all 40 classes ───────────────────────
PLANT_FALLBACK = {
    "Aloevera": {
        "common_name": "Aloe Vera", "scientific_name": "Aloe barbadensis miller",
        "description": "A succulent plant with thick, fleshy leaves containing a clear gel. Native to the Arabian Peninsula, it thrives in tropical and subtropical climates worldwide.",
        "medicinal_uses": ["Burns and wound healing", "Skin moisturizer", "Digestive aid", "Anti-inflammatory treatment", "Sunburn relief"],
        "pros": ["Widely available", "Easy to grow at home", "Multiple topical uses", "Natural skin soother"],
        "cons": ["Latex can cause diarrhea if ingested", "May cause allergic reactions in some", "Avoid oral use during pregnancy"],
        "parts_used": ["Leaf gel", "Leaf latex"],
        "interesting_fact": "Aloe vera gel is composed of 99% water and has been used medicinally for over 6,000 years."
    },
    "Amla": {
        "common_name": "Indian Gooseberry", "scientific_name": "Phyllanthus emblica",
        "description": "A deciduous tree native to tropical southeastern Asia, producing small greenish-yellow fruits that are among the richest natural sources of Vitamin C.",
        "medicinal_uses": ["Boosts immunity", "Improves digestion", "Promotes hair growth", "Anti-aging antioxidant", "Manages diabetes"],
        "pros": ["Extremely high Vitamin C content", "Supports liver health", "Improves skin and hair", "Anti-diabetic properties"],
        "cons": ["Sour taste may be unpleasant", "May lower blood sugar too much with medication", "Can cause acidity in excess"],
        "parts_used": ["Fruit", "Leaves", "Bark", "Seeds"],
        "interesting_fact": "One Amla fruit contains 20x more Vitamin C than an orange."
    },
    "Amruta_Balli": {
        "common_name": "Giloy / Guduchi", "scientific_name": "Tinospora cordifolia",
        "description": "A climbing shrub native to India, known in Ayurveda as 'Amrita' meaning nectar of immortality. It is an important immunomodulator.",
        "medicinal_uses": ["Boosts immunity", "Manages fever and dengue", "Anti-diabetic", "Treats arthritis", "Detoxification"],
        "pros": ["Powerful immunomodulator", "Adaptogenic properties", "Reduces chronic fever", "Anti-inflammatory"],
        "cons": ["May lower blood sugar excessively", "Can cause constipation", "Avoid in autoimmune disorders"],
        "parts_used": ["Stem", "Leaves", "Roots"],
        "interesting_fact": "Giloy is called 'the root of immortality' in Ayurveda and is one of the three Amrit plants."
    },
    "Arali": {
        "common_name": "Oleander", "scientific_name": "Nerium oleander",
        "description": "An ornamental shrub with beautiful pink or white flowers, native to the Mediterranean region. Despite its beauty, it is one of the most toxic plants known.",
        "medicinal_uses": ["Traditionally used for heart conditions (under strict supervision)", "Skin disease treatment in traditional medicine", "Rat poison historically", "Anti-cancer research compound", "Insecticide preparation"],
        "pros": ["Active compounds researched for cancer therapy", "Traditional cardiac uses", "Drought-resistant ornamental"],
        "cons": ["Extremely toxic — all parts are poisonous", "Can be fatal if ingested", "Causes cardiac arrest in high doses", "Never self-medicate"],
        "parts_used": ["Leaves (medicinal research only)", "Bark (traditional use only)"],
        "interesting_fact": "All parts of Oleander are highly toxic — even honey made from its nectar can cause poisoning."
    },
    "Ashoka": {
        "common_name": "Ashoka Tree", "scientific_name": "Saraca asoca",
        "description": "A sacred tree in Indian culture with dark green leaves and bright orange-red flowers. It is widely used in Ayurveda, especially for women's health.",
        "medicinal_uses": ["Uterine disorders and menstrual irregularities", "Anti-inflammatory", "Bleeding disorders", "Skin conditions", "Digestive complaints"],
        "pros": ["Excellent uterine tonic", "Natural anti-inflammatory", "Rich in flavonoids and tannins", "Well-documented Ayurvedic use"],
        "cons": ["Avoid during pregnancy", "Limited modern clinical trials", "May interact with hormonal medications"],
        "parts_used": ["Bark", "Flowers", "Leaves", "Seeds"],
        "interesting_fact": "Ashoka means 'without grief' in Sanskrit — it is considered a sacred tree in Buddhism and Hinduism."
    },
    "Ashwagandha": {
        "common_name": "Indian Ginseng / Winter Cherry", "scientific_name": "Withania somnifera",
        "description": "A small shrub with yellow flowers native to India and Southeast Asia. One of the most important herbs in Ayurveda, classified as an adaptogen.",
        "medicinal_uses": ["Reduces stress and anxiety", "Boosts testosterone and fertility", "Improves brain function", "Anti-inflammatory", "Manages blood sugar"],
        "pros": ["Clinically proven adaptogen", "Improves sleep quality", "Boosts athletic performance", "Neuroprotective properties"],
        "cons": ["May cause drowsiness", "Avoid during pregnancy", "Can interact with thyroid medications", "Large doses cause GI upset"],
        "parts_used": ["Root", "Leaves", "Berries"],
        "interesting_fact": "Ashwagandha means 'smell of horse' in Sanskrit — referring to its smell and the belief it gives horse-like strength."
    },
    "Avacado": {
        "common_name": "Avocado", "scientific_name": "Persea americana",
        "description": "A tree native to south-central Mexico producing a large berry with a single seed. The fruit is rich in healthy fats and has numerous medicinal properties.",
        "medicinal_uses": ["Heart health improvement", "Anti-inflammatory", "Wound healing (leaf extracts)", "Blood sugar regulation", "Skin nourishment"],
        "pros": ["Rich in healthy monounsaturated fats", "High potassium content", "Anti-inflammatory compounds", "Promotes eye health"],
        "cons": ["High in calories", "Avocado leaves toxic to some animals", "Seed extracts can be harmful", "May trigger latex-fruit syndrome"],
        "parts_used": ["Fruit", "Leaves", "Seed (limited use)", "Bark"],
        "interesting_fact": "Avocado is technically a berry, and it contains more potassium than a banana."
    },
    "Bamboo": {
        "common_name": "Bamboo", "scientific_name": "Bambusoideae spp.",
        "description": "The world's fastest-growing plant, bamboo belongs to the grass family and is widely used in traditional Asian medicine for various ailments.",
        "medicinal_uses": ["Respiratory disorders treatment", "Anti-inflammatory", "Fever reduction", "Digestive aid", "Bone strengthening"],
        "pros": ["High silica content for bone health", "Anti-bacterial properties", "Young shoots are nutritious", "Sustainable resource"],
        "cons": ["Some species contain cyanogenic glycosides", "Raw shoots must be cooked", "Limited clinical evidence"],
        "parts_used": ["Young shoots", "Leaves", "Roots", "Silica extract"],
        "interesting_fact": "Bamboo can grow up to 91 cm (3 feet) in a single day — the fastest growing plant on Earth."
    },
    "Basale": {
        "common_name": "Malabar Spinach", "scientific_name": "Basella alba",
        "description": "A fast-growing succulent vine used as a leafy vegetable and medicinal plant across tropical Asia and Africa. Known for its mucilaginous texture.",
        "medicinal_uses": ["Constipation relief (laxative)", "Anti-inflammatory", "Wound healing", "Anemia treatment (iron-rich)", "Cooling agent in fevers"],
        "pros": ["Excellent iron and calcium source", "Natural laxative", "Anti-ulcer properties", "Easily grown in home gardens"],
        "cons": ["Oxalates may affect kidney stone patients", "Laxative effect can be strong", "Limited pharmacological studies"],
        "parts_used": ["Leaves", "Stems", "Fruit"],
        "interesting_fact": "Malabar spinach is unrelated to regular spinach but contains more iron and calcium per serving."
    },
    "Betel": {
        "common_name": "Betel Leaf", "scientific_name": "Piper betle",
        "description": "A vine belonging to the Piperaceae family, native to Southeast Asia. The leaves are widely chewed with areca nut and used in traditional medicine.",
        "medicinal_uses": ["Oral hygiene and antiseptic", "Digestive stimulant", "Wound healing", "Anti-fungal treatment", "Respiratory congestion relief"],
        "pros": ["Potent antiseptic properties", "Anti-bacterial action", "Stimulates digestion", "Traditional wound dressing"],
        "cons": ["Chewing with areca nut is carcinogenic", "Can stain teeth", "Addictive when used with tobacco", "May cause mouth cancer over time"],
        "parts_used": ["Leaves"],
        "interesting_fact": "Betel leaf has been chewed in Asia for over 2,000 years and is part of important cultural ceremonies."
    },
    "Betel_Nut": {
        "common_name": "Areca Nut / Betel Nut", "scientific_name": "Areca catechu",
        "description": "A palm tree native to Southeast Asia, producing seeds (nuts) that are widely chewed across Asia. It is a mild stimulant with significant health risks.",
        "medicinal_uses": ["Anthelmintic (expels worms)", "Digestive stimulant", "Saliva stimulation", "Traditional treatment for dry mouth", "Tapeworm treatment in veterinary use"],
        "pros": ["Effective anthelmintic", "Stimulant properties", "Traditional digestive use"],
        "cons": ["Classified as Group 1 carcinogen by IARC", "Causes oral submucous fibrosis", "Highly addictive", "Associated with oral and esophageal cancer"],
        "parts_used": ["Seed (nut)", "Husk", "Flower"],
        "interesting_fact": "Over 600 million people worldwide chew areca nut — making it the 4th most used psychoactive substance after tobacco, alcohol, and caffeine."
    },
    "Brahmi": {
        "common_name": "Brahmi / Water Hyssop", "scientific_name": "Bacopa monnieri",
        "description": "A creeping herb native to wetlands of Southern and Eastern India. One of the most celebrated brain tonics in Ayurveda.",
        "medicinal_uses": ["Memory enhancement", "Reduces anxiety and stress", "ADHD management", "Anti-epileptic", "Anti-oxidant neuroprotection"],
        "pros": ["Clinically proven cognitive enhancer", "Safe for long-term use", "Reduces cortisol levels", "Improves learning and memory"],
        "cons": ["May cause nausea on empty stomach", "Slows heart rate slightly", "Avoid with sedative medications", "Results take 8-12 weeks"],
        "parts_used": ["Whole plant", "Leaves", "Stem"],
        "interesting_fact": "Brahmi is named after Brahma, the Hindu god of creation — reflecting its reputation for enhancing intellect and creativity."
    },
    "Castor": {
        "common_name": "Castor Plant", "scientific_name": "Ricinus communis",
        "description": "A fast-growing plant native to East Africa and India. Its seeds yield castor oil, one of the most commercially important vegetable oils.",
        "medicinal_uses": ["Laxative (castor oil)", "Skin moisturizer", "Inducing labor (traditional)", "Anti-inflammatory poultices", "Hair growth stimulation"],
        "pros": ["Effective natural laxative", "Ricinoleic acid has anti-inflammatory action", "Promotes hair and skin health", "Antifungal properties"],
        "cons": ["Seeds contain deadly ricin toxin", "Castor oil can cause severe diarrhea", "Never consume raw seeds", "Avoid during pregnancy (abortifacient)"],
        "parts_used": ["Seeds (oil)", "Leaves", "Roots"],
        "interesting_fact": "Castor seeds contain ricin, one of the most toxic naturally occurring substances — just 1mg per kg body weight can be fatal."
    },
    "Curry_Leaf": {
        "common_name": "Curry Leaf", "scientific_name": "Murraya koenigii",
        "description": "A tropical tree native to India and Sri Lanka. Its aromatic leaves are widely used in South Indian cooking and traditional medicine.",
        "medicinal_uses": ["Anti-diabetic properties", "Improves digestion", "Anti-diarrheal", "Promotes hair growth", "Reduces cholesterol"],
        "pros": ["Rich in antioxidants", "Anti-diabetic alkaloids", "Promotes hair growth and color", "Anti-bacterial properties"],
        "cons": ["May interact with diabetes medications", "Some people experience contact dermatitis", "Limited clinical trials"],
        "parts_used": ["Leaves", "Bark", "Roots", "Fruit"],
        "interesting_fact": "Curry leaves are not related to curry powder — but they are the original 'curry' flavor in South Indian cuisine."
    },
    "Doddapatre": {
        "common_name": "Indian Borage / Mexican Mint", "scientific_name": "Plectranthus amboinicus",
        "description": "A succulent perennial herb with large, thick aromatic leaves. Widely used in Indian folk medicine for respiratory and digestive complaints.",
        "medicinal_uses": ["Cold and cough remedy", "Throat infection treatment", "Digestive disorders", "Anti-inflammatory", "Skin infections"],
        "pros": ["Easily available home remedy", "Strong antimicrobial properties", "Safe for children (in small doses)", "Effective for respiratory ailments"],
        "cons": ["May cause contact dermatitis", "Strong smell not universally liked", "Avoid excessive intake during pregnancy"],
        "parts_used": ["Leaves", "Stem"],
        "interesting_fact": "Doddapatre leaves mixed with honey and ginger is a traditional remedy that rivals commercial cough syrups in effectiveness."
    },
    "Ekka": {
        "common_name": "Giant Calotrope / Madar", "scientific_name": "Calotropis gigantea",
        "description": "A large shrub native to Cambodia, Bangladesh, India, and Malaysia. It produces white or purple flowers and is used extensively in Ayurveda.",
        "medicinal_uses": ["Skin disease treatment", "Anti-inflammatory", "Fever reduction", "Dental pain relief", "Wound healing"],
        "pros": ["Potent anti-inflammatory latex", "Antifungal and antibacterial", "Used in snake bite treatment (traditional)", "Rich in bioactive compounds"],
        "cons": ["Highly toxic if ingested", "Latex can cause skin irritation", "Eye contact with latex causes blindness risk", "Never self-medicate"],
        "parts_used": ["Root bark", "Latex", "Leaves", "Flowers"],
        "interesting_fact": "The silky fibers from Calotropis seed pods were used as a kapok substitute in World War II life jackets."
    },
    "Ganike": {
        "common_name": "Turkey Berry / Wild Eggplant", "scientific_name": "Solanum torvum",
        "description": "A bushy perennial plant native to the Caribbean and Central America, now widespread in tropical regions. Used extensively in cuisine and traditional medicine.",
        "medicinal_uses": ["Anemia treatment (iron-rich)", "Anti-diabetic properties", "Treats kidney disorders", "Anti-microbial", "Menstrual regulation"],
        "pros": ["High iron content combats anemia", "Antioxidant-rich berries", "Anti-hyperglycemic properties", "Diuretic action for kidney health"],
        "cons": ["Unripe berries contain solanine (toxic)", "Bitter taste requires preparation", "May lower blood pressure too much"],
        "parts_used": ["Fruit", "Leaves", "Roots"],
        "interesting_fact": "Turkey berry is a staple ingredient in Ghanaian palm nut soup and Thai green curry."
    },
    "Gauva": {
        "common_name": "Guava", "scientific_name": "Psidium guajava",
        "description": "A tropical tree native to Central America and Mexico, producing sweet fragrant fruits. Both the fruit and leaves have significant medicinal properties.",
        "medicinal_uses": ["Anti-diarrheal (leaf tea)", "Blood sugar regulation", "Immune system boost (Vitamin C)", "Anti-inflammatory", "Oral health and gum treatment"],
        "pros": ["Leaves clinically proven for diarrhea", "4x more Vitamin C than oranges", "Anti-diabetic quercetin content", "Improves heart health"],
        "cons": ["Excessive leaf tea may cause constipation", "May interfere with diabetes drugs", "Seeds can accumulate in gut"],
        "parts_used": ["Fruit", "Leaves", "Bark", "Roots"],
        "interesting_fact": "Guava leaf tea is a WHO-recommended remedy for diarrhea in developing countries."
    },
    "Geranium": {
        "common_name": "Rose Geranium", "scientific_name": "Pelargonium graveolens",
        "description": "A perennial shrub native to South Africa, famous for its fragrant rose-scented leaves. Widely used in aromatherapy and herbal medicine.",
        "medicinal_uses": ["Anxiety and stress relief (aromatherapy)", "Anti-fungal skin treatment", "Wound healing", "Insect repellent", "Hormone balancing (traditional)"],
        "pros": ["Pleasant aromatic properties", "Proven antifungal activity", "Effective insect repellent", "Mood-enhancing in aromatherapy"],
        "cons": ["May cause contact dermatitis", "Phototoxic in some preparations", "Avoid concentrated oil near eyes"],
        "parts_used": ["Leaves", "Flowers", "Essential oil"],
        "interesting_fact": "Geranium essential oil is used in high-end perfumery as a rose oil substitute and costs a fraction of true rose oil."
    },
    "Henna": {
        "common_name": "Henna / Mehndi", "scientific_name": "Lawsonia inermis",
        "description": "A flowering shrub native to tropical and subtropical regions of Africa, South Asia, and the Middle East. The leaves produce a natural dye used for millennia.",
        "medicinal_uses": ["Anti-fungal skin treatment", "Cooling agent for fevers (feet application)", "Wound healing", "Anti-bacterial", "Headache relief (forehead application)"],
        "pros": ["Natural antifungal and antibacterial", "Cooling properties reduce fever", "Safe natural hair dye", "Anti-inflammatory compounds"],
        "cons": ["Black henna contains PPD (carcinogen)", "May cause allergic reactions", "Avoid on broken skin", "Stains are permanent on fabric"],
        "parts_used": ["Leaves", "Bark", "Seeds", "Flowers"],
        "interesting_fact": "Henna has been used for body art for over 5,000 years — ancient Egyptian mummies have been found with henna-stained nails."
    },
    "Hibiscus": {
        "common_name": "Hibiscus / Roselle", "scientific_name": "Hibiscus rosa-sinensis",
        "description": "A large flowering shrub with bright red flowers, native to East Asia. One of the most widely used medicinal and cosmetic plants globally.",
        "medicinal_uses": ["Lowers blood pressure", "Reduces cholesterol", "Promotes hair growth", "Liver protection", "Anti-diabetic effects"],
        "pros": ["Clinically proven blood pressure reduction", "Rich in Vitamin C and antioxidants", "Anti-aging properties", "Promotes thick lustrous hair"],
        "cons": ["May lower blood pressure too much with medication", "Avoid during pregnancy (emmenagogue)", "May affect estrogen levels", "Can cause drowsiness"],
        "parts_used": ["Flowers", "Leaves", "Roots"],
        "interesting_fact": "Hibiscus tea is the national drink of Egypt and one of the most consumed herbal teas worldwide."
    },
    "Honge": {
        "common_name": "Pongamia / Indian Beech", "scientific_name": "Millettia pinnata",
        "description": "A medium-sized tree native to South and Southeast Asia, valued for its oil-rich seeds, nitrogen-fixing properties, and medicinal uses.",
        "medicinal_uses": ["Skin diseases treatment", "Anti-rheumatic", "Anti-parasitic (wounds)", "Dental pain relief", "Anti-ulcer"],
        "pros": ["Potent antifungal and antibacterial oil", "Treats chronic skin conditions", "Anti-inflammatory compounds", "Biofuel source"],
        "cons": ["Pongamia oil is bitter and toxic if ingested", "Seeds are poisonous", "Skin irritant in some individuals"],
        "parts_used": ["Seed oil", "Leaves", "Bark", "Flowers"],
        "interesting_fact": "Honge oil is one of India's leading candidates for biodiesel — it can run diesel engines directly without refining."
    },
    "Insulin": {
        "common_name": "Insulin Plant / Costus", "scientific_name": "Costus pictus",
        "description": "A perennial herb native to Mexico, widely cultivated in India for its remarkable blood sugar-lowering properties. The leaves are said to mimic insulin action.",
        "medicinal_uses": ["Type 2 diabetes management", "Blood sugar regulation", "Diuretic action", "Anti-microbial", "Kidney stone prevention"],
        "pros": ["Proven hypoglycemic activity", "Easy to grow at home", "No major side effects in normal doses", "Rich in corosolic acid"],
        "cons": ["May dangerously lower blood sugar with insulin drugs", "Not a substitute for medical diabetes treatment", "Limited human clinical trials"],
        "parts_used": ["Leaves", "Rhizome"],
        "interesting_fact": "The insulin plant's leaves are typically eaten raw (1-2 leaves daily) by diabetic patients in Kerala, India as a traditional remedy."
    },
    "Jasmine": {
        "common_name": "Jasmine", "scientific_name": "Jasminum officinale",
        "description": "A climbing shrub native to Central Asia and China with intensely fragrant white flowers. Used in perfumery, aromatherapy, and traditional medicine.",
        "medicinal_uses": ["Anxiety and depression relief (aromatherapy)", "Antiseptic wound treatment", "Anti-spasmodic", "Improves sleep quality", "Lactation stimulation"],
        "pros": ["Proven anxiolytic in aromatherapy", "Natural antiseptic", "Uplifts mood", "Anti-inflammatory properties"],
        "cons": ["May cause allergic reactions", "Avoid concentrated oil during pregnancy", "Can trigger headaches in sensitive individuals"],
        "parts_used": ["Flowers", "Leaves", "Essential oil"],
        "interesting_fact": "It takes approximately 8 million jasmine flowers to produce 1kg of jasmine essential oil, making it one of the most expensive oils in the world."
    },
    "Lemon": {
        "common_name": "Lemon", "scientific_name": "Citrus limon",
        "description": "A small evergreen tree native to South Asia producing yellow acidic fruits. Rich in Vitamin C and citric acid, used extensively in both culinary and medicinal applications.",
        "medicinal_uses": ["Immunity boosting (Vitamin C)", "Digestive aid", "Kidney stone prevention", "Anti-bacterial", "Weight management aid"],
        "pros": ["Extremely high Vitamin C content", "Alkalizing effect on body despite acidity", "Anti-bacterial limonene", "Supports iron absorption"],
        "cons": ["Erodes tooth enamel over time", "Can worsen acid reflux", "May interact with certain medications (like statins)"],
        "parts_used": ["Fruit juice", "Peel / Zest", "Leaves", "Essential oil"],
        "interesting_fact": "Lemon trees can produce up to 600 pounds of lemons per year, and they never stop fruiting — they produce all year round."
    },
    "Lemon_grass": {
        "common_name": "Lemongrass", "scientific_name": "Cymbopogon citratus",
        "description": "A tall perennial grass native to South Asia with a strong lemon scent. Widely used in Asian cuisine and traditional medicine for its anti-microbial properties.",
        "medicinal_uses": ["Anti-fungal treatment", "Fever reduction", "Digestive cramping relief", "Anxiety reduction (aromatherapy)", "Anti-bacterial infections"],
        "pros": ["Potent anti-fungal citral content", "Effective insect repellent", "Reduces anxiety and improves sleep", "Anti-inflammatory"],
        "cons": ["May cause skin irritation undiluted", "Avoid during pregnancy", "Can lower blood sugar excessively"],
        "parts_used": ["Leaves (stalks)", "Essential oil", "Roots"],
        "interesting_fact": "Lemongrass is not related to lemons at all — it gets its citrus scent from citral, the same compound found in lemon peel."
    },
    "Mango": {
        "common_name": "Mango", "scientific_name": "Mangifera indica",
        "description": "A large tropical tree native to South Asia producing the 'king of fruits.' Beyond its culinary value, the leaves, bark, and seed contain significant medicinal compounds.",
        "medicinal_uses": ["Anti-diabetic (mango leaf tea)", "Anti-diarrheal (bark)", "Gum disease treatment", "Anti-inflammatory", "Kidney stone treatment (seed)"],
        "pros": ["Rich in mangiferin (powerful antioxidant)", "Mango leaves lower blood sugar", "Anti-cancer compounds in peel", "Anti-microbial bark"],
        "cons": ["Mango sap causes contact dermatitis", "High sugar content in fruit", "Unripe mango causes throat irritation", "Mango leaf tea may interact with diabetes drugs"],
        "parts_used": ["Leaves", "Bark", "Seed", "Fruit peel"],
        "interesting_fact": "Mango is the national fruit of India, Pakistan, and the Philippines — and it has been cultivated in India for over 4,000 years."
    },
    "Mint": {
        "common_name": "Mint / Peppermint", "scientific_name": "Mentha × piperita",
        "description": "A hybrid mint species produced by crossing watermint and spearmint. One of the world's oldest known herbal medicines with a distinctive cooling sensation.",
        "medicinal_uses": ["Irritable bowel syndrome relief", "Headache treatment (topical)", "Nausea and indigestion relief", "Respiratory decongestant", "Anti-bacterial oral hygiene"],
        "pros": ["Clinically proven for IBS", "Natural decongestant menthol", "Broad spectrum anti-microbial", "Headache relief when applied topically"],
        "cons": ["Can worsen acid reflux (relaxes esophageal sphincter)", "Avoid pure menthol near infants' faces", "May interact with cyclosporine"],
        "parts_used": ["Leaves", "Essential oil", "Stems"],
        "interesting_fact": "Ancient Romans and Greeks crowned themselves with peppermint to signal hospitality and used it to flavor wines and sauces."
    },
    "Nagadali": {
        "common_name": "Sarpagandha / Indian Snakeroot", "scientific_name": "Rauvolfia serpentina",
        "description": "A perennial shrub native to India used in Ayurveda for thousands of years. It contains reserpine, which revolutionized modern treatment of hypertension.",
        "medicinal_uses": ["High blood pressure treatment", "Anxiety and insomnia relief", "Anti-psychotic (traditional)", "Snake bite treatment (traditional)", "Fever reduction"],
        "pros": ["Contains reserpine — first modern antihypertensive drug", "Powerful sedative", "Clinically proven blood pressure reduction"],
        "cons": ["Causes depression with long-term use", "Numerous drug interactions", "Contraindicated in depression patients", "Can cause Parkinson-like symptoms"],
        "parts_used": ["Roots", "Bark"],
        "interesting_fact": "Reserpine extracted from this plant was the world's first antihypertensive pharmaceutical drug, introduced in the 1950s."
    },
    "Neem": {
        "common_name": "Neem", "scientific_name": "Azadirachta indica",
        "description": "A fast-growing tree native to South Asia, known as the 'Village Pharmacy' of India. Over 130 biologically active compounds have been identified from it.",
        "medicinal_uses": ["Anti-bacterial skin treatment", "Dental hygiene (neem twigs)", "Anti-malarial", "Blood sugar regulation", "Anti-fungal treatment"],
        "pros": ["Broad-spectrum antimicrobial", "Natural pesticide (azadirachtin)", "Anti-diabetic properties", "Promotes oral health"],
        "cons": ["Toxic to children in large doses", "Neem oil can damage kidneys if ingested", "May reduce fertility", "Bitter taste limits use"],
        "parts_used": ["Leaves", "Bark", "Seeds", "Oil", "Twigs"],
        "interesting_fact": "A single neem tree absorbs CO₂ equivalent to 10 cars — it is also used as a natural pesticide on 5 continents."
    },
    "Nithyapushpa": {
        "common_name": "Periwinkle / Vinca", "scientific_name": "Catharanthus roseus",
        "description": "A flowering plant native to Madagascar with pink or white blooms. Despite its ornamental appearance, it has produced two of the most important anti-cancer drugs ever discovered.",
        "medicinal_uses": ["Anti-cancer (vinblastine and vincristine from this plant)", "Diabetes management", "Blood pressure lowering", "Wound healing", "Anti-bacterial"],
        "pros": ["Source of life-saving cancer drugs", "Anti-diabetic alkaloids", "Easily grown ornamental", "Anti-microbial properties"],
        "cons": ["Highly toxic if ingested (all parts)", "Causes neurological damage in overdose", "Never self-medicate with raw plant"],
        "parts_used": ["Leaves", "Roots", "Flowers"],
        "interesting_fact": "Vincristine and vinblastine, derived from this plant, are used to treat childhood leukemia with a cure rate over 90%."
    },
    "Nooni": {
        "common_name": "Noni", "scientific_name": "Morinda citrifolia",
        "description": "A small tree native to Southeast Asia and Australasia with distinctive pungent fruit. Used in traditional Polynesian medicine for over 2,000 years.",
        "medicinal_uses": ["Immune system boosting", "Anti-inflammatory", "Pain relief", "Anti-bacterial infections", "Anti-cancer research compound"],
        "pros": ["Rich in iridoids (antioxidants)", "Immune modulating properties", "Anti-inflammatory scopoletin content", "Traditional use well-documented"],
        "cons": ["High potassium — dangerous for kidney patients", "Reported liver toxicity cases", "Strong unpleasant smell and taste", "Drug interactions possible"],
        "parts_used": ["Fruit", "Leaves", "Roots", "Bark"],
        "interesting_fact": "Noni fruit is sometimes called 'starvation fruit' — it was eaten as a last resort food during famines in Polynesia due to its awful taste."
    },
    "Pappaya": {
        "common_name": "Papaya", "scientific_name": "Carica papaya",
        "description": "A fast-growing tree native to Mexico and Central America, producing large orange fruits. Both the fruit and leaves have well-documented medicinal properties.",
        "medicinal_uses": ["Dengue fever platelet count increase (leaf juice)", "Digestive enzyme (papain)", "Anti-parasitic", "Wound debridement", "Anti-inflammatory"],
        "pros": ["Papain enzyme aids protein digestion", "Clinically studied for dengue treatment", "Rich in antioxidant lycopene", "Anti-bacterial latex"],
        "cons": ["Unripe papaya is abortifacient — avoid in pregnancy", "Latex can cause allergic reactions", "May interact with blood thinners"],
        "parts_used": ["Fruit", "Leaves", "Seeds", "Latex", "Roots"],
        "interesting_fact": "Papaya leaf juice has been shown in clinical studies to significantly increase platelet count in dengue fever patients."
    },
    "Pepper": {
        "common_name": "Black Pepper", "scientific_name": "Piper nigrum",
        "description": "A flowering vine native to South India, producing the world's most traded spice. Black pepper has been used as both a spice and medicine since ancient times.",
        "medicinal_uses": ["Improves nutrient bioavailability (piperine)", "Anti-inflammatory", "Digestive stimulant", "Anti-bacterial", "Respiratory congestion relief"],
        "pros": ["Piperine dramatically increases absorption of curcumin and other nutrients", "Anti-oxidant properties", "Stimulates digestive enzymes", "Anti-bacterial action"],
        "cons": ["May irritate stomach lining in excess", "Can cause heartburn", "May interact with some medications (bioavailability enhancer)"],
        "parts_used": ["Fruit (peppercorns)", "Essential oil"],
        "interesting_fact": "Black pepper was so valuable in medieval Europe it was used as currency and called 'black gold' — Attila the Hun demanded 3,000 pounds of pepper as ransom."
    },
    "Pomegranate": {
        "common_name": "Pomegranate", "scientific_name": "Punica granatum",
        "description": "A fruit-bearing deciduous shrub native to the region from Iran to the Himalayas. One of the oldest known fruits, with exceptional antioxidant properties.",
        "medicinal_uses": ["Heart disease prevention", "Anti-inflammatory", "Anti-cancer research", "Memory improvement", "Anti-diabetic properties"],
        "pros": ["3x the antioxidant power of red wine", "Proven to lower blood pressure", "Anti-cancer punicalagins", "Improves memory and cognitive function"],
        "cons": ["May interact with blood pressure medications", "High in natural sugar", "Pomegranate juice can interact with statins (like grapefruit)"],
        "parts_used": ["Fruit arils", "Rind/Peel", "Bark", "Flowers", "Roots"],
        "interesting_fact": "Pomegranate is one of the oldest fruits — it was found in Egyptian tombs and is mentioned in the Bible, the Quran, and the Odyssey."
    },
    "Raktachandini": {
        "common_name": "Red Sandalwood", "scientific_name": "Pterocarpus santalinus",
        "description": "A slow-growing tree endemic to the Eastern Ghats of India. The heartwood has a distinctive red color and is used in Ayurveda and traditional medicine.",
        "medicinal_uses": ["Anti-diabetic", "Anti-inflammatory", "Skin disorders treatment", "Liver protection", "Fever reduction"],
        "pros": ["Potent anti-diabetic activity", "Anti-oxidant pterostilbene content", "Skin brightening properties", "Hepatoprotective effects"],
        "cons": ["Endangered species — use sustainably", "May lower blood sugar excessively with medication", "Limited clinical human trials"],
        "parts_used": ["Heartwood", "Wood powder"],
        "interesting_fact": "Red Sandalwood is so valuable it is protected by the Indian government — illegal logging is punishable by imprisonment."
    },
    "Rose": {
        "common_name": "Rose", "scientific_name": "Rosa damascena",
        "description": "The Damascus rose, native to Syria, is the most medicinally important rose species. Its petals are steam-distilled to produce rose water and rose essential oil.",
        "medicinal_uses": ["Anti-anxiety and antidepressant (aromatherapy)", "Anti-inflammatory skin treatment", "Digestive complaints (rose water)", "Headache relief", "Menstrual pain relief"],
        "pros": ["Clinically proven anxiolytic aroma", "Anti-inflammatory flavonoids", "Vitamin C in rose hips", "Antibacterial rose water"],
        "cons": ["Expensive essential oil can be adulterated", "May cause allergies in sensitive individuals", "Rose hip seeds have fine hairs that irritate GI tract"],
        "parts_used": ["Petals", "Rose hip (fruit)", "Essential oil", "Rose water"],
        "interesting_fact": "It takes 60,000 rose flowers (about 1 full acre of roses) to produce just 30ml of rose essential oil."
    },
    "Sapota": {
        "common_name": "Sapodilla / Chiku", "scientific_name": "Manilkara zapota",
        "description": "A long-lived tropical evergreen tree native to southern Mexico and Central America, producing sweet brown fruits with medicinal properties.",
        "medicinal_uses": ["Energy booster (high glucose content)", "Anti-diarrheal (bark tannins)", "Anti-viral properties", "Bone strengthening (calcium)", "Digestive fiber source"],
        "pros": ["Excellent source of dietary fiber", "Rich in vitamins A and C", "Anti-diarrheal bark extract", "High energy fruit for convalescence"],
        "cons": ["High sugar content (diabetics should limit)", "Unripe fruit contains saponins (toxic)", "Latex can cause mouth sores"],
        "parts_used": ["Fruit", "Bark", "Seeds", "Latex"],
        "interesting_fact": "Sapodilla latex (chicle) was the original ingredient in chewing gum — it was the main chewing gum material before synthetic gums were invented."
    },
    "Tulasi": {
        "common_name": "Holy Basil / Tulsi", "scientific_name": "Ocimum tenuiflorum",
        "description": "A sacred aromatic shrub native to the Indian subcontinent, revered in Hinduism as the 'Queen of Herbs.' One of the most important plants in Ayurveda.",
        "medicinal_uses": ["Respiratory disorders (cough, cold, asthma)", "Stress and anxiety reduction (adaptogen)", "Anti-bacterial and anti-viral", "Fever reduction", "Blood sugar regulation"],
        "pros": ["Powerful adaptogen reduces cortisol", "Broad-spectrum antimicrobial", "Clinically proven for stress relief", "Easily grown in home garden"],
        "cons": ["May thin blood — avoid before surgery", "Can lower blood sugar with diabetes medication", "Avoid high doses in pregnancy", "May reduce fertility in some studies"],
        "parts_used": ["Leaves", "Seeds (Sabja)", "Roots", "Essential oil"],
        "interesting_fact": "Tulsi is so sacred in Hinduism that it is found in almost every Hindu household — it is believed to purify the air and protect the family."
    },
    "Wood_sorel": {
        "common_name": "Wood Sorrel", "scientific_name": "Oxalis acetosella",
        "description": "A delicate clover-like plant found in woodlands and shaded areas across Europe and Asia. Its leaves have a pleasant sour taste due to oxalic acid.",
        "medicinal_uses": ["Anti-scurvy (Vitamin C source historically)", "Digestive aid", "Fever reduction", "Wound cleansing (leaf poultice)", "Diuretic"],
        "pros": ["Natural Vitamin C source", "Cooling and thirst-quenching", "Anti-inflammatory properties", "Edible wild green"],
        "cons": ["High oxalate content harmful to kidneys", "Avoid in kidney stones patients", "Toxic in very large quantities", "Can cause GI upset in excess"],
        "parts_used": ["Leaves", "Stems", "Flowers"],
        "interesting_fact": "Wood sorrel was widely used by indigenous peoples and early explorers as an anti-scurvy remedy long before Vitamin C was discovered."
    }
}


def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


@main_bp.route('/')
def index():
    return render_template('index_2.html')   # FIXED: was index_2.html


@main_bp.route('/api/info', methods=['GET'])
def api_info():
    try:
        loader = get_model_loader()
        model_info = loader.get_model_info()
        return jsonify({
            'success': True,
            'api_version': '1.0',
            'system': 'Medicinal Plant Identification',
            'model_info': model_info,
            'timestamp': datetime.now().isoformat()
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@main_bp.route('/api/predict', methods=['POST'])
def predict():
    start_time = time.time()

    if 'file' not in request.files:
        return jsonify({'success': False, 'error': 'No file provided'}), 400

    file = request.files['file']

    if file.filename == '':
        return jsonify({'success': False, 'error': 'No file selected'}), 400

    # ── Accept files with no extension (common with Android camera captures) ──
    if file.filename and not allowed_file(file.filename):
        # Try to detect from MIME type as fallback
        mime = file.content_type or ''
        if not any(t in mime for t in ['jpeg', 'jpg', 'png']):
            return jsonify({'success': False, 'error': f'Invalid file type. Allowed: jpg, jpeg, png'}), 400

    apply_preprocessing = request.form.get('preprocess', 'true').lower() == 'true'
    debug_mode = request.form.get('debug', 'false').lower() == 'true'

    filepath = None
    try:
        # ── Save uploaded file ───────────────────────────────────────────────
        original_name = secure_filename(file.filename) if file.filename else 'upload'
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S_%f')

        # Ensure .jpg extension if filename has none (Android camera quirk)
        if '.' not in original_name:
            original_name += '.jpg'

        unique_filename = f"{timestamp}_{original_name}"

        upload_folder = 'uploads'
        os.makedirs(upload_folder, exist_ok=True)

        filepath = os.path.join(upload_folder, unique_filename)
        file.save(filepath)

        print(f"\n{'='*70}")
        print(f"Processing: {unique_filename}")
        print(f"{'='*70}")
        print("Step 1: Image uploaded")

        if apply_preprocessing:
            print("Step 2: Applying preprocessing pipeline...")
        else:
            print("Step 2: Simple preprocessing (resize + normalize only)")

        loader = get_model_loader()
        predictions = loader.predict(
            filepath,
            apply_preprocessing=apply_preprocessing,
            debug=debug_mode
        )

        print(f"Step 3: Running Inception-V3 prediction")
        print(f"✓ Prediction: {predictions['ensemble']['plant']} ({predictions['ensemble']['percentage']})")
        print(f"{'='*70}\n")

        processing_time = time.time() - start_time

        if not debug_mode:
            try:
                os.remove(filepath)
            except Exception:
                pass

        return jsonify({
            'success': True,
            'predictions': predictions,
            'processing_time': f"{processing_time:.2f}s",
            'preprocessing_applied': apply_preprocessing,
            'debug_mode': debug_mode,
            'timestamp': datetime.now().isoformat()
        })

    except Exception as e:
        if filepath:
            try:
                os.remove(filepath)
            except Exception:
                pass

        print(f"\n✗ Error in /api/predict: {str(e)}\n")
        import traceback
        traceback.print_exc()

        return jsonify({
            'success': False,
            'error': str(e),
            'processing_time': f"{time.time() - start_time:.2f}s"
        }), 500


@main_bp.route('/api/plant-info', methods=['POST'])
def plant_info():
    """
    Fetch plant info — tries Anthropic API first, falls back to built-in data.
    """
    data = request.get_json()
    if not data or 'plant_name' not in data:
        return jsonify({'success': False, 'error': 'plant_name required'}), 400

    plant_name = data['plant_name'].strip()
    api_key = os.environ.get('ANTHROPIC_API_KEY', '').strip()

    # ── Try Anthropic API first ──────────────────────────────────────────────
    if api_key and not api_key.startswith('sk-ant-your'):
        prompt = (
            f'Give detailed medicinal plant information for "{plant_name}" as a JSON object '
            f'with exactly these keys:\n'
            '{\n'
            '  "common_name": "string",\n'
            '  "scientific_name": "string",\n'
            '  "description": "string - 2-3 sentence overview",\n'
            '  "medicinal_uses": ["5 specific uses"],\n'
            '  "pros": ["4 key benefits"],\n'
            '  "cons": ["3 cautions or side effects"],\n'
            '  "parts_used": ["plant parts"],\n'
            '  "interesting_fact": "one notable fact"\n'
            '}'
        )

        payload = json.dumps({
            "model": "claude-sonnet-4-20250514",
            "max_tokens": 1000,
            "system": "You are a medicinal plants expert. Return ONLY valid JSON, no markdown, no backticks.",
            "messages": [{"role": "user", "content": prompt}]
        }).encode('utf-8')

        req = urllib.request.Request(
            "https://api.anthropic.com/v1/messages",
            data=payload,
            headers={
                "Content-Type": "application/json",
                "x-api-key": api_key,
                "anthropic-version": "2023-06-01"
            },
            method="POST"
        )

        try:
            with urllib.request.urlopen(req, timeout=30) as resp:
                result = json.loads(resp.read().decode('utf-8'))
                raw = ''.join(b.get('text', '') for b in result.get('content', []))
                clean = raw.replace('```json', '').replace('```', '').strip()
                plant_data = json.loads(clean)
                print(f"✓ Plant info fetched from Anthropic API for: {plant_name}")
                return jsonify({'success': True, 'data': plant_data, 'source': 'api'})

        except urllib.error.HTTPError as e:
            err_body = e.read().decode('utf-8', errors='ignore')[:120]
            print(f"Anthropic API HTTP Error {e.code}: {err_body} — using fallback for: {plant_name}")
        except urllib.error.URLError as e:
            print(f"Anthropic API URL Error: {e.reason} — using fallback for: {plant_name}")
        except json.JSONDecodeError as e:
            print(f"Anthropic API JSON parse error: {e} — using fallback for: {plant_name}")
        except Exception as e:
            print(f"Anthropic API unexpected error: {str(e)[:80]} — using fallback for: {plant_name}")

    # ── Fallback: built-in data — exact match ────────────────────────────────
    fallback = PLANT_FALLBACK.get(plant_name)

    # Case-insensitive match
    if not fallback:
        for key, val in PLANT_FALLBACK.items():
            if key.lower() == plant_name.lower():
                fallback = val
                break

    # Partial match (e.g. "Curry Leaf" vs "Curry_Leaf")
    if not fallback:
        normalized = plant_name.lower().replace(' ', '_').replace('-', '_')
        for key, val in PLANT_FALLBACK.items():
            if key.lower().replace(' ', '_') == normalized:
                fallback = val
                break

    if fallback:
        print(f"✓ Plant info served from fallback for: {plant_name}")
        return jsonify({'success': True, 'data': fallback, 'source': 'fallback'})

    # Generic fallback for unrecognised plants
    generic = {
        "common_name": plant_name,
        "scientific_name": "Species under review",
        "description": (
            f"{plant_name} is a medicinal plant used in traditional medicine across South Asia. "
            "It has been used for generations for its therapeutic properties."
        ),
        "medicinal_uses": [
            "Traditional folk medicine", "Anti-inflammatory applications",
            "Digestive health", "Immune support", "Topical wound treatment"
        ],
        "pros": [
            "Used in traditional medicine", "Natural origin",
            "Minimal processing required", "Widely available in native regions"
        ],
        "cons": [
            "Consult a doctor before use",
            "Individual reactions may vary",
            "Avoid during pregnancy without guidance"
        ],
        "parts_used": ["Leaves", "Roots", "Bark"],
        "interesting_fact": (
            f"{plant_name} is one of the 40 medicinal plants identified and studied "
            "in this project's dataset."
        )
    }

    print(f"✓ Generic fallback served for unrecognised plant: {plant_name}")
    return jsonify({'success': True, 'data': generic, 'source': 'generic'})


@main_bp.route('/api/classes', methods=['GET'])
def get_classes():
    try:
        loader = get_model_loader()
        return jsonify({
            'success': True,
            'classes': loader.class_names,
            'count': len(loader.class_names)
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@main_bp.route('/api/health', methods=['GET'])
def health_check():
    try:
        loader = get_model_loader()
        return jsonify({
            'success': True,
            'status': 'healthy',
            'models_loaded': len(loader.models),
            'timestamp': datetime.now().isoformat()
        })
    except Exception as e:
        return jsonify({'success': False, 'status': 'unhealthy', 'error': str(e)}), 500




# ─── GPS / Scan logging ──────────────────────────────────────────────────────
import sqlite3, pathlib

DB_PATH = pathlib.Path(__file__).parent.parent / 'data' / 'scans.db'

def get_db():
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(str(DB_PATH))
    conn.row_factory = sqlite3.Row
    conn.execute("""
        CREATE TABLE IF NOT EXISTS scans (
            id        INTEGER PRIMARY KEY AUTOINCREMENT,
            plant     TEXT,
            confidence REAL,
            lat       REAL,
            lng       REAL,
            accuracy  REAL,
            user_agent TEXT,
            created_at TEXT DEFAULT (datetime('now'))
        )
    """)
    conn.commit()
    return conn


@main_bp.route('/api/log-scan', methods=['POST'])
def log_scan():
    """Called from frontend after every prediction + optional GPS."""
    try:
        d = request.get_json(force=True) or {}
        plant      = d.get('plant', 'Unknown')
        confidence = float(d.get('confidence', 0))
        lat        = d.get('lat')
        lng        = d.get('lng')
        accuracy   = d.get('accuracy')
        ua         = request.headers.get('User-Agent', '')[:200]

        conn = get_db()
        conn.execute(
            "INSERT INTO scans (plant,confidence,lat,lng,accuracy,user_agent) VALUES (?,?,?,?,?,?)",
            (plant, confidence, lat, lng, accuracy, ua)
        )
        conn.commit()
        conn.close()
        print(f"✓ Scan logged: {plant} ({confidence:.1f}%) lat={lat} lng={lng}")
        return jsonify({'success': True})
    except Exception as e:
        print(f"✗ log-scan error: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500


@main_bp.route('/admin')
def admin_dashboard():
    """Simple admin map — view all user scans with GPS."""
    try:
        conn = get_db()
        scans = conn.execute(
            "SELECT * FROM scans ORDER BY created_at DESC LIMIT 500"
        ).fetchall()
        conn.close()
        rows = [dict(s) for s in scans]

        # Build map markers JS
        markers_js = "var markers = " + json.dumps([
            {"plant": r["plant"], "confidence": r["confidence"],
             "lat": r["lat"], "lng": r["lng"],
             "time": r["created_at"]}
            for r in rows if r["lat"] and r["lng"]
        ]) + ";"

        total       = len(rows)
        with_gps    = sum(1 for r in rows if r["lat"])
        species_set = len(set(r["plant"] for r in rows))

        # Recent 20 for table
        recent = rows[:20]

        html = f"""<!DOCTYPE html>
<html><head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>Admin — Plant Scan Map</title>
<link rel="stylesheet" href="https://unpkg.com/leaflet@1.9.4/dist/leaflet.css"/>
<script src="https://unpkg.com/leaflet@1.9.4/dist/leaflet.js"></script>
<style>
*{{margin:0;padding:0;box-sizing:border-box;font-family:sans-serif}}
body{{background:#f0f4f0}}
.top{{background:#0d3d22;color:#fff;padding:14px 20px;display:flex;align-items:center;gap:16px}}
.top h1{{font-size:1em;font-weight:700}}
.stats{{display:flex;gap:8px;padding:12px 16px;background:#fff;border-bottom:1px solid #dde5d8}}
.stat{{background:#f0f9f4;border-radius:10px;padding:10px 16px;text-align:center;flex:1}}
.stat-v{{font-size:1.5em;font-weight:700;color:#1a6b3c}}
.stat-l{{font-size:0.65em;color:#6b7280;text-transform:uppercase;letter-spacing:0.5px}}
#map{{height:340px;border-bottom:1px solid #dde5d8}}
.table-wrap{{padding:12px 16px;overflow-x:auto}}
h2{{font-size:0.8em;font-weight:700;text-transform:uppercase;color:#6b7280;letter-spacing:0.8px;margin-bottom:8px}}
table{{width:100%;border-collapse:collapse;font-size:0.8em}}
th{{background:#f0f4f0;padding:7px 10px;text-align:left;color:#374151;font-weight:600}}
td{{padding:7px 10px;border-bottom:1px solid #eee;color:#374151}}
.conf-hi{{color:#16a34a;font-weight:700}}
.conf-mid{{color:#d97706;font-weight:700}}
.conf-lo{{color:#dc2626;font-weight:700}}
.dl-btn{{display:inline-block;background:#1a6b3c;color:#fff;padding:8px 18px;border-radius:8px;font-size:0.82em;font-weight:600;text-decoration:none;margin-bottom:12px}}
</style>
</head><body>
<div class="top">
  <span style="font-size:1.4em">🌿</span>
  <h1>Medicinal Plant — Admin Scan Dashboard</h1>
  <span style="margin-left:auto;font-size:0.78em;opacity:0.7">Plant Pharmers · SIH 2023</span>
</div>
<div class="stats">
  <div class="stat"><div class="stat-v">{total}</div><div class="stat-l">Total Scans</div></div>
  <div class="stat"><div class="stat-v">{with_gps}</div><div class="stat-l">GPS Tagged</div></div>
  <div class="stat"><div class="stat-v">{species_set}</div><div class="stat-l">Species</div></div>
</div>
<div id="map"></div>
<div class="table-wrap">
  <a class="dl-btn" href="/admin/export-csv">⬇ Download All as CSV</a>
  <h2>Recent 20 Scans</h2>
  <table>
    <tr><th>Plant</th><th>Confidence</th><th>Location</th><th>Time</th></tr>
    {"".join(
        f'<tr><td>{r["plant"].replace("_", " ")}</td>'
        f'<td class="conf-{"hi" if r["confidence"]>=60 else "mid" if r["confidence"]>=40 else "lo"}">{r["confidence"]:.1f}%</td>'
        + ('<td><a href="https://maps.google.com/?q=' + str(r["lat"]) + ',' + str(r["lng"]) + '">📍 View</a></td>' if r["lat"] else '<td>-</td>')
        + f'<td style="white-space:nowrap">{(r["created_at"] or "")[:16]}</td></tr>'
        for r in recent
    )}
  </table>
</div>
<script>
{markers_js}
var map = L.map('map').setView([20.5937, 78.9629], 5);
L.tileLayer('https://{{s}}.tile.openstreetmap.org/{{z}}/{{x}}/{{y}}.png',{{
    attribution:'© OpenStreetMap'
}}).addTo(map);
markers.forEach(function(m){{
    var conf = m.confidence;
    var color = conf>=60?'#16a34a':conf>=40?'#d97706':'#dc2626';
    var circle = L.circleMarker([m.lat,m.lng],{{
        radius:8, fillColor:color, color:'#fff',
        weight:2, opacity:1, fillOpacity:0.85
    }}).addTo(map);
    circle.bindPopup('<b>'+m.plant.replace(/_/g,' ')+'</b><br>'+conf.toFixed(1)+'% confidence<br>'+m.time);
}});
if(markers.length>0){{
    var lats=markers.map(function(m){{return m.lat;}});
    var lngs=markers.map(function(m){{return m.lng;}});
    map.fitBounds([[Math.min(...lats),Math.min(...lngs)],[Math.max(...lats),Math.max(...lngs)]],{{padding:[20,20]}});
}}
</script>
</body></html>"""
        return html
    except Exception as e:
        return f"<pre>Admin error: {e}</pre>", 500


@main_bp.route('/admin/export-csv')
def export_csv():
    """Download all scan data as CSV."""
    try:
        import io
        conn = get_db()
        scans = conn.execute("SELECT * FROM scans ORDER BY created_at DESC").fetchall()
        conn.close()
        output = io.StringIO()
        output.write("id,plant,confidence,lat,lng,accuracy,user_agent,created_at\n")
        for r in scans:
            output.write(f'{r["id"]},"{r["plant"]}",{r["confidence"] or ""},')
            output.write(f'{r["lat"] or ""},{r["lng"] or ""},{r["accuracy"] or ""},')
            ua = (r["user_agent"] or "").replace('"', '')
            output.write(f'"{ua}",{r["created_at"]}\n')
        from flask import Response
        return Response(
            output.getvalue(),
            mimetype='text/csv',
            headers={"Content-Disposition": "attachment;filename=plant_scans.csv"}
        )
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@main_bp.errorhandler(404)
def not_found(error):
    return jsonify({'success': False, 'error': 'Endpoint not found'}), 404


@main_bp.errorhandler(500)
def internal_error(error):
    return jsonify({'success': False, 'error': 'Internal server error'}), 500