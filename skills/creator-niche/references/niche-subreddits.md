# Niche → subreddits + seed keywords

Used by `creator-niche` to build the `--subs` argument for `trends.py niche`.
Pick the closest row; for hybrids (e.g. "vegan fitness"), take 2 subs from each row, max 5.
Pass subs comma-separated, without `r/`. Seeds become extra `--q` probes in `--deep` runs.

If the niche is not listed: WebSearch `best subreddits for <niche>` once, keep 3 subs that
look active, and tell the user which you chose.

| Niche | Subreddits (`--subs`) | Seed keywords |
|-------|-----------------------|---------------|
| Fitness (general) | fitness,bodyweightfitness,GYM,xxfitness | workout plan, beginner workout, progressive overload |
| Weight loss | loseit,1500isplenty,progresspics,CICO | calorie deficit, weight loss plateau, high protein meals |
| Bodybuilding / lifting | bodybuilding,weightroom,powerlifting,naturalbodybuilding | hypertrophy, bulking, creatine |
| Running | running,AdvancedRunning,C25K,trailrunning | couch to 5k, marathon training, running shoes |
| Yoga / mobility | yoga,flexibility,posture | yoga for beginners, hip mobility, morning stretch |
| Keto / low-carb | keto,ketorecipes,ketoscience | keto diet, keto recipes, keto flu |
| Vegan / plant-based | vegan,PlantBasedDiet,veganrecipes | vegan protein, plant based meals |
| Cooking / recipes | Cooking,recipes,EatCheapAndHealthy,MealPrepSunday | easy dinner, meal prep, air fryer recipes |
| Baking | Baking,Breadit,Sourdough | sourdough starter, baking tips |
| Personal finance | personalfinance,financialindependence,povertyfinance,Frugal | budgeting, emergency fund, credit score |
| Investing | investing,stocks,Bogleheads,dividends | index funds, ETF, dividend investing |
| Crypto | CryptoCurrency,Bitcoin,ethereum | bitcoin price, crypto wallet |
| Real estate | RealEstate,FirstTimeHomeBuyer,realestateinvesting | first time home buyer, mortgage rates |
| Side hustles / online income | sidehustle,Entrepreneur,passive_income,WorkOnline | side hustle ideas, make money online |
| Small business / startups | smallbusiness,startups,Entrepreneur,SaaS | startup ideas, small business marketing |
| Marketing / social media | marketing,socialmedia,content_marketing,DigitalMarketing | content strategy, instagram growth |
| SEO / blogging | SEO,juststart,Blogging | keyword research, blog traffic |
| Content creation / YouTube | NewTubers,youtubers,PartneredYoutube,Tiktokhelp | youtube algorithm, grow on tiktok |
| AI tools | ChatGPT,artificial,singularity,LocalLLaMA | ai tools, chatgpt prompts, ai agents |
| Programming | programming,learnprogramming,webdev,cscareerquestions | learn to code, coding interview |
| Productivity | productivity,getdisciplined,Notion,ObsidianMD | productivity tips, notion template, time blocking |
| Careers / job search | jobs,careerguidance,resumes,recruitinghell | resume tips, job interview, career change |
| Tech / gadgets | gadgets,Android,apple,buildapc | best phone, gaming pc build |
| Gaming | gaming,pcgaming,NintendoSwitch,PS5 | best games, game review |
| Photography | photography,AskPhotography,analog | camera settings, best camera for beginners |
| Video editing / filmmaking | VideoEditing,Filmmakers,premiere,davinciresolve | color grading, editing tips |
| Fashion (men) | malefashionadvice,streetwear,BuyItForLife | outfit ideas, capsule wardrobe |
| Fashion (women) | femalefashionadvice,fashion,capsulewardrobe | outfit ideas, fall outfits |
| Skincare / beauty | SkincareAddiction,AsianBeauty,MakeupAddiction | skincare routine, retinol, acne |
| Haircare | Hair,curlyhair,malehairadvice | hair growth, curly hair routine |
| Parenting | Parenting,NewParents,Mommit,daddit | toddler tantrums, baby sleep |
| Relationships / dating | relationship_advice,dating_advice,dating | dating tips, red flags |
| Mental health / self-improvement | selfimprovement,DecidingToBeBetter,Anxiety,getdisciplined | anxiety tips, habits, discipline |
| Travel | travel,solotravel,onebag,TravelHacks | travel tips, budget travel, packing list |
| Home / interior design | HomeImprovement,malelivingspace,InteriorDesign,DIY | room makeover, small apartment ideas |
| Gardening / plants | gardening,houseplants,vegetablegardening | indoor plants, raised bed garden |
| Pets (dogs) | dogs,puppy101,Dogtraining | puppy training, dog food |
| Pets (cats) | cats,CatAdvice,CatTraining | cat behavior, kitten care |
| Cars | cars,whatcarshouldIbuy,electricvehicles,MechanicAdvice | best used cars, EV vs hybrid |
| Books / reading | books,suggestmeabook,Fantasy,booksuggestions | book recommendations, reading habit |
| Education / study | GetStudying,college,languagelearning,studytips | study tips, learn a language |
| Music production | WeAreTheMusicMakers,edmproduction,musicproduction | music production, mixing tips |
| Sustainability / minimalism | ZeroWaste,minimalism,simpleliving | zero waste swaps, declutter |
| Outdoors / camping | CampingandHiking,hiking,Ultralight | camping gear, beginner hikes |
| Home workout | bodyweightfitness,homegym,xxfitness | home workout, no equipment workout, home gym |

Notes:
- Reddit top-of-week RSS returns only titles; treat them as audience-question and debate
  signals, not as engagement counts (none are fetched).
- Reddit rate-limits bursts (HTTP 429). Keep `--subs` to 3-5; if all 429, continue with
  News + Suggest + HN and say Reddit was unavailable.
