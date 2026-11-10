// Sources suivies par Radar IA. type : rss (RSS/Atom), yt (chaîne YouTube), ytnom (chaîne à retrouver par son nom),
// hfpapers (papiers du jour Hugging Face), trending (GitHub Trending), ghsearch (nouveaux dépôts IA), release (versions d'un dépôt).
// filtre : true = source généraliste, on ne garde que ce qui parle d'IA.
export const SOURCES = [
  // Laboratoires et éditeurs
  { id: "openai", nom: "OpenAI", famille: "Laboratoires", type: "rss", url: "https://openai.com/news/rss.xml", poids: 1.3 },
  { id: "deepmind", nom: "Google DeepMind", famille: "Laboratoires", type: "rss", url: "https://deepmind.google/blog/rss.xml", poids: 1.3 },
  { id: "googleai", nom: "Google AI", famille: "Laboratoires", type: "rss", url: "https://blog.google/technology/ai/rss/", poids: 1.1 },
  { id: "msr", nom: "Microsoft Research", famille: "Laboratoires", type: "rss", url: "https://www.microsoft.com/en-us/research/feed/", poids: 1.0 },
  { id: "hfblog", nom: "Hugging Face", famille: "Modèles ouverts", type: "rss", url: "https://huggingface.co/blog/feed.xml", poids: 1.2 },
  { id: "nvidia", nom: "NVIDIA Developer", famille: "Matériel", type: "rss", url: "https://developer.nvidia.com/blog/feed", poids: 1.0 },
  // Presse anglophone
  { id: "mittr", nom: "MIT Technology Review", famille: "Presse EN", type: "rss", url: "https://www.technologyreview.com/topic/artificial-intelligence/feed", poids: 1.1 },
  { id: "ars", nom: "Ars Technica", famille: "Presse EN", type: "rss", url: "https://arstechnica.com/ai/feed/", poids: 1.1 },
  { id: "techcrunch", nom: "TechCrunch AI", famille: "Presse EN", type: "rss", url: "https://techcrunch.com/category/artificial-intelligence/feed/", poids: 1.0 },
  { id: "verge", nom: "The Verge AI", famille: "Presse EN", type: "rss", url: "https://www.theverge.com/rss/ai-artificial-intelligence/index.xml", poids: 1.0 },
  { id: "wired", nom: "Wired AI", famille: "Presse EN", type: "rss", url: "https://www.wired.com/feed/tag/ai/latest/rss", poids: 0.9 },
  { id: "decoder", nom: "The Decoder", famille: "Presse EN", type: "rss", url: "https://the-decoder.com/feed/", poids: 1.1 },
  // Presse francophone
  { id: "actuia", nom: "ActuIA", famille: "Presse FR", type: "rss", url: "https://www.actuia.com/feed/", poids: 1.1 },
  { id: "numerama", nom: "Numerama", famille: "Presse FR", type: "rss", url: "https://www.numerama.com/feed/", poids: 0.9, filtre: true },
  { id: "frandroid", nom: "Frandroid", famille: "Presse FR", type: "rss", url: "https://www.frandroid.com/feed", poids: 0.8, filtre: true },
  { id: "next", nom: "Next", famille: "Presse FR", type: "rss", url: "https://next.ink/feed/", poids: 0.9, filtre: true },
  { id: "lesnum", nom: "Les Numériques", famille: "Presse FR", type: "rss", url: "https://www.lesnumeriques.com/rss.xml", poids: 0.8, filtre: true },
  // Recherche
  { id: "hfpapers", nom: "Hugging Face Papers", famille: "Recherche", type: "hfpapers", url: "https://huggingface.co/api/daily_papers", poids: 1.0 },
  // Écosystème logiciel (versions)
  { id: "ollama", nom: "Ollama", famille: "Écosystème", type: "release", url: "https://github.com/ollama/ollama/releases.atom", poids: 1.1 },
  { id: "vllm", nom: "vLLM", famille: "Écosystème", type: "release", url: "https://github.com/vllm-project/vllm/releases.atom", poids: 0.9 },
  { id: "comfyui", nom: "ComfyUI", famille: "Écosystème", type: "release", url: "https://github.com/comfyanonymous/ComfyUI/releases.atom", poids: 0.9 },
  { id: "lmstudio", nom: "LM Studio", famille: "Écosystème", type: "rss", url: "https://lmstudio.ai/rss.xml", poids: 1.0 },
  // Ce qui fait vraiment parler
  { id: "hn", nom: "Hacker News", famille: "Communauté", type: "hn", url: "https://hn.algolia.com/api/v1/search", poids: 1.2 },
  { id: "r-localllama", nom: "Reddit LocalLLaMA", famille: "Communauté", type: "rss", url: "https://www.reddit.com/r/LocalLLaMA/top/.rss?t=day", poids: 1.1 },
  { id: "r-stablediffusion", nom: "Reddit StableDiffusion", famille: "Communauté", type: "rss", url: "https://www.reddit.com/r/StableDiffusion/top/.rss?t=day", poids: 1.0 },
  // Newsletters et blogs spécialisés
  { id: "willison", nom: "Simon Willison", famille: "Spécialistes", type: "rss", url: "https://simonwillison.net/atom/everything/", poids: 1.2 },
  { id: "importai", nom: "Import AI", famille: "Spécialistes", type: "rss", url: "https://importai.substack.com/feed", poids: 1.1 },
  { id: "latentspace", nom: "Latent Space", famille: "Spécialistes", type: "rss", url: "https://www.latent.space/feed", poids: 1.1 },
  { id: "interconnects", nom: "Interconnects", famille: "Spécialistes", type: "rss", url: "https://www.interconnects.ai/feed", poids: 1.1 },
  { id: "lastweekinai", nom: "Last Week in AI", famille: "Spécialistes", type: "rss", url: "https://lastweekin.ai/feed", poids: 1.0 },
  { id: "marktechpost", nom: "MarkTechPost", famille: "Spécialistes", type: "rss", url: "https://www.marktechpost.com/feed/", poids: 0.9 },
  { id: "venturebeat", nom: "VentureBeat AI", famille: "Presse EN", type: "rss", url: "https://venturebeat.com/category/ai/feed/", poids: 1.0 },
  // Modèles qui sortent (Hugging Face, tous types)
  { id: "hf-modeles", nom: "Hugging Face — modèles en tendance", famille: "Modèles", type: "hfmodeles", url: "https://huggingface.co/api/models?sort=trendingScore&limit=100", poids: 1.2 },
  { id: "hf-libres", nom: "Hugging Face — modèles non censurés", famille: "Modèles", type: "hflibres", url: "https://huggingface.co/api/models", poids: 1.0 },
  // GitHub
  { id: "trending", nom: "GitHub Trending (jour)", famille: "GitHub", type: "trending", url: "https://github.com/trending?since=daily", poids: 1.0 },
  { id: "trending-semaine", nom: "GitHub Trending (semaine)", famille: "GitHub", type: "trending", url: "https://github.com/trending?since=weekly", poids: 1.0 },
  { id: "ghsearch", nom: "Nouveaux dépôts IA", famille: "GitHub", type: "ghsearch", url: "https://api.github.com/search/repositories", poids: 1.0 },
  // Vidéos — anglais (identifiants connus)
  { id: "yt-mattwolfe", nom: "Matt Wolfe", famille: "Vidéos EN", type: "yt", canal: "UChpleBmo18P08aKCIgti38g", poids: 1.0 },
  { id: "yt-berman", nom: "Matthew Berman", famille: "Vidéos EN", type: "yt", canal: "UCawZsQWqfGSbCI5yjkdVkTA", poids: 1.0 },
  { id: "yt-aiexplained", nom: "AI Explained", famille: "Vidéos EN", type: "yt", canal: "UCNJ1Ymd5yFuUPtn21xtRbbw", poids: 1.2 },
  { id: "yt-kilcher", nom: "Yannic Kilcher", famille: "Vidéos EN", type: "yt", canal: "UCZHmQk67mSJgfCCTn7xBfew", poids: 1.0 },
  { id: "yt-2mp", nom: "Two Minute Papers", famille: "Vidéos EN", type: "yt", canal: "UCbfYPyITQ-7l4upoX8nvctg", poids: 1.0 },
  // Vidéos — français
  { id: "yt-visionia", nom: "Vision IA", famille: "Vidéos FR", type: "yt", canal: "UCyc03X3uRuxM9n7fyRH_gIw", poids: 1.1 },
  { id: "yt-paul", nom: "Paul Automatise", famille: "Vidéos FR", type: "ytnom", recherche: "Paul Automatise", poids: 1.1 },
  { id: "yt-nerdy", nom: "Nerdy Kings", famille: "Vidéos FR", type: "ytnom", recherche: "Nerdy Kings", poids: 1.0 },
  { id: "yt-labia", nom: "Le Lab IA", famille: "Vidéos FR", type: "ytnom", recherche: "Le Lab IA", poids: 1.0 },
  { id: "yt-ialocale", nom: "IA Locale Facile", famille: "Vidéos FR", type: "ytnom", recherche: "IA Locale Facile", poids: 1.0 },
  { id: "yt-renaud", nom: "Renaud Dékode", famille: "Vidéos FR", type: "ytnom", recherche: "Renaud Dékode", poids: 1.0 },
  // Vidéos — tes abonnements YouTube qui parlent d'IA (export Google du 10.11.2026)
  { id: "yt-ai-edge", nom: "AI Edge", famille: "Vidéos EN", type: "yt", canal: "UC-PQKtrPhk3JXyjUleBLgQQ", poids: 0.9, abo: true },
  { id: "yt-arty-free-ai-dev-tools", nom: "Arty | Free AI Dev Tools", famille: "Vidéos EN", type: "yt", canal: "UC1A36hOgd-sF4vJYxM13jdQ", poids: 0.9, abo: true },
  { id: "yt-preporato-ai-for-enginee", nom: "Preporato | AI for Engineers", famille: "Vidéos EN", type: "yt", canal: "UC1Kh2LHv34aB7Dgr_D1SkSg", poids: 0.9, abo: true },
  { id: "yt-tech-friend-aj", nom: "Tech Friend AJ", famille: "Vidéos EN", type: "yt", canal: "UC1RO76_HDT13u-lPXOA0t9A", poids: 0.9, abo: true },
  { id: "yt-ai-voice-agents", nom: "AI Voice Agents", famille: "Vidéos EN", type: "yt", canal: "UC1ltEEIACLvc1fUl7BTK__w", poids: 0.9, abo: true },
  { id: "yt-duncan-rogoff-learn-clau", nom: "Duncan Rogoff | Learn Claude Code", famille: "Vidéos EN", type: "yt", canal: "UC37JpWP5PxLSma2lh79HU9A", poids: 0.9, abo: true },
  { id: "yt-nick-puru-ai-automation", nom: "Nick Puru | AI Automation", famille: "Vidéos EN", type: "yt", canal: "UC4FK5DEcMLB3CyJcbJfZEJA", poids: 0.9, abo: true },
  { id: "yt-melvynx", nom: "Melvynx", famille: "Vidéos FR", type: "yt", canal: "UC5HDIVwuqoIuKKw-WbQ4CvA", poids: 0.9, abo: true },
  { id: "yt-ben-kimball-ai", nom: "Ben Kimball Ai", famille: "Vidéos EN", type: "yt", canal: "UC5cY7agID9yvdezCBYGTraQ", poids: 0.9, abo: true },
  { id: "yt-pliny-the-prompter", nom: "Pliny the Prompter", famille: "Vidéos EN", type: "yt", canal: "UC5obt8DBGtc_RPdeA6YR_Tw", poids: 0.9, abo: true },
  { id: "yt-bilawal-sidhu", nom: "Bilawal Sidhu", famille: "Vidéos EN", type: "yt", canal: "UC7bGK0A1weWfNaRfO0hGVdg", poids: 0.9, abo: true },
  { id: "yt-mark-gadala-maria", nom: "Mark Gadala-Maria", famille: "Vidéos EN", type: "yt", canal: "UC7dDxcJywuKqzvsoJLCM4bQ", poids: 0.9, abo: true },
  { id: "yt-junk-gpu-lab", nom: "Junk GPU Lab", famille: "Vidéos EN", type: "yt", canal: "UC8DzlJK_eouv24Jfo9QHhMg", poids: 0.9, abo: true },
  { id: "yt-bart-slodyczka", nom: "Bart Slodyczka", famille: "Vidéos EN", type: "yt", canal: "UC8F7X90NDmMr1mGx8897r_A", poids: 0.9, abo: true },
  { id: "yt-ai-revolution-en-fran-ai", nom: "AI Revolution en Français", famille: "Vidéos FR", type: "yt", canal: "UC92vtIxo1ZoXyF_yqJWFiJQ", poids: 0.9, abo: true },
  { id: "yt-github-awesome", nom: "Github Awesome", famille: "Vidéos EN", type: "yt", canal: "UC9Rrud-8CaHokDtK9FszvRg", poids: 0.9, abo: true },
  { id: "yt-automate-with-marc-ai-au", nom: "Automate with Marc | AI Automation", famille: "Vidéos EN", type: "yt", canal: "UC9ayeuN4-0rtFYIrf-xUDLw", poids: 0.9, abo: true },
  { id: "yt-networkchuck", nom: "NetworkChuck", famille: "Vidéos EN", type: "yt", canal: "UC9x0AN7BWHpCDHSm9NiJFJQ", poids: 0.9, abo: true },
  { id: "yt-michael-automates", nom: "Michael Automates", famille: "Vidéos EN", type: "yt", canal: "UCC0O5FKSMcjzrvOUa08hS_A", poids: 0.9, abo: true },
  { id: "yt-doctor-chain-crypto-ai-a", nom: "Doctor Chain — Crypto, AI & Automation", famille: "Vidéos EN", type: "yt", canal: "UCCnx7GVWQpeiaZ2Zj1n4GVg", poids: 0.9, abo: true },
  { id: "yt-specs-the-prompter", nom: "Specs the Prompter", famille: "Vidéos EN", type: "yt", canal: "UCDzBP-MVl72XdWePOlGORxg", poids: 0.9, abo: true },
  { id: "yt-ai-samson", nom: "AI Samson", famille: "Vidéos EN", type: "yt", canal: "UCED3hlYdD0SlCff7jJ8tF3Q", poids: 0.9, abo: true },
  { id: "yt-sebastian-hardy-ai-marke", nom: "Sebastian Hardy | AI Marketing", famille: "Vidéos EN", type: "yt", canal: "UCG5HFY9PXYeIHSyRgML2tvg", poids: 0.9, abo: true },
  { id: "yt-julian-goldie-seo", nom: "Julian Goldie SEO", famille: "Vidéos EN", type: "yt", canal: "UCGpsgNbzdF7BECCVbB1COHw", poids: 0.9, abo: true },
  { id: "yt-mark-kashef", nom: "Mark Kashef", famille: "Vidéos EN", type: "yt", canal: "UCHkzp52CldSPZqU5T49mOnA", poids: 0.9, abo: true },
  { id: "yt-stephen-g-pope", nom: "Stephen G. Pope", famille: "Vidéos EN", type: "yt", canal: "UCIg2taLnC9X6LRP1k3kukOA", poids: 0.9, abo: true },
  { id: "yt-ai-chip-insider", nom: "AI Chip Insider", famille: "Vidéos EN", type: "yt", canal: "UCIjlWscEzGTBgLza3FPH9NQ", poids: 0.9, abo: true },
  { id: "yt-shubham-sharma", nom: "Shubham SHARMA", famille: "Vidéos EN", type: "yt", canal: "UCLKx4-_XO5sR0AO0j8ye7zQ", poids: 0.9, abo: true },
  { id: "yt-moon-dev", nom: "Moon Dev", famille: "Vidéos EN", type: "yt", canal: "UCN7D80fY9xMYu5mHhUhXEFw", poids: 0.9, abo: true },
  { id: "yt-outskill", nom: "Outskill", famille: "Vidéos EN", type: "yt", canal: "UCNssyoLJiA2oB5xM7XjxmJA", poids: 0.9, abo: true },
  { id: "yt-ai-with-abhijay-master-g", nom: "AI With Abhijay | Master Gemini, ChatGPT & Claude", famille: "Vidéos EN", type: "yt", canal: "UCODkOkw7WmA7pA6qa4csdJw", poids: 0.9, abo: true },
  { id: "yt-eric-djavid-ia-et-automa", nom: "Eric Djavid - IA et Automatisations", famille: "Vidéos FR", type: "yt", canal: "UCOx3YU1EemFPDRp6LOpIDVQ", poids: 0.9, abo: true },
  { id: "yt-david-ondrej", nom: "David Ondrej", famille: "Vidéos EN", type: "yt", canal: "UCPGrgwfbkjTIgPoOh2q1BAg", poids: 0.9, abo: true },
  { id: "yt-the-fast-track-ai", nom: "The Fast Track AI", famille: "Vidéos EN", type: "yt", canal: "UCSf17OP2BqTF66I_7S7RIrw", poids: 0.9, abo: true },
  { id: "yt-nick-automates", nom: "Nick Automates", famille: "Vidéos EN", type: "yt", canal: "UCUX5AP1M0mBbgUi_WklPbOQ", poids: 0.9, abo: true },
  { id: "yt-unefilleia", nom: "unefilleia", famille: "Vidéos FR", type: "yt", canal: "UCUaPm7H9l1AvDLEcqyjqaoA", poids: 0.9, abo: true },
  { id: "yt-visionx-lab", nom: "VisionX Lab", famille: "Vidéos EN", type: "yt", canal: "UCVCa-_J1CLBzpT52EwuZ3yQ", poids: 0.9, abo: true },
  { id: "yt-underscore", nom: "Underscore_", famille: "Vidéos FR", type: "yt", canal: "UCWedHS9qKebauVIK2J7383g", poids: 0.9, abo: true },
  { id: "yt-julian-goldie-rundown", nom: "Julian Goldie Rundown", famille: "Vidéos FR", type: "yt", canal: "UCWwIigj-ohiwH9rl8y2g8vA", poids: 0.9, abo: true },
  { id: "yt-ailithic", nom: "AIlithic", famille: "Vidéos FR", type: "yt", canal: "UCX0eEvwLCHwkxReqwRY0fLw", poids: 0.9, abo: true },
  { id: "yt-shabbir-noor-ai-for-oper", nom: "Shabbir Noor | AI For Operators", famille: "Vidéos EN", type: "yt", canal: "UCXenik3GxthoPs5xJcbxuPw", poids: 0.9, abo: true },
  { id: "yt-project-claude", nom: "Project Claude", famille: "Vidéos EN", type: "yt", canal: "UCYR7d32CC91TrfdQ2CAZryw", poids: 0.9, abo: true },
  { id: "yt-mark-kashef-ai-for-busin", nom: "Mark Kashef | AI For Business Owners", famille: "Vidéos EN", type: "yt", canal: "UCYUp-OY4EvX-dvKBmtsrjOQ", poids: 0.9, abo: true },
  { id: "yt-micode", nom: "Micode", famille: "Vidéos FR", type: "yt", canal: "UCYnvxJ-PKiGXo_tYXpWAC-w", poids: 0.9, abo: true },
  { id: "yt-telenewswire-ai-news-wit", nom: "Telenewswire (AI News without fuss)", famille: "Vidéos EN", type: "yt", canal: "UCZqOmHaclAZ0-7XV-fOlJJQ", poids: 0.9, abo: true },
  { id: "yt-next-token-news", nom: "Next Token News", famille: "Vidéos EN", type: "yt", canal: "UCfKZ4CNHv0SQVM4YZX5njZQ", poids: 0.9, abo: true },
  { id: "yt-jay-e-robonuggets", nom: "Jay E | RoboNuggets", famille: "Vidéos EN", type: "yt", canal: "UCgscS8mBsQZ5sFRkJIFWD7Q", poids: 0.9, abo: true },
  { id: "yt-sabrina-ramonov", nom: "Sabrina Ramonov 🍄", famille: "Vidéos EN", type: "yt", canal: "UCiGWNa6QK6CiKPvv5-YPv8g", poids: 0.9, abo: true },
  { id: "yt-le-raphin-astuces-ia", nom: "Le Raphiné - Astuces IA", famille: "Vidéos FR", type: "yt", canal: "UCicK1mPlkztZyKjFRC6uKIg", poids: 0.9, abo: true },
  { id: "yt-thomas-stachowiak-builde", nom: "Thomas Stachowiak | Builder IA", famille: "Vidéos FR", type: "yt", canal: "UCjOaNT8je6xn1jseW_KyY0g", poids: 0.9, abo: true },
  { id: "yt-ai-honeycove", nom: "AI Honeycove", famille: "Vidéos EN", type: "yt", canal: "UCkrTgKhXqEt_L9woc43K0BA", poids: 0.9, abo: true },
  { id: "yt-j-b-vibe-marketer", nom: "J.B. | Vibe Marketer", famille: "Vidéos EN", type: "yt", canal: "UCl557o_cV0XBm_o7aGXELkQ", poids: 0.9, abo: true },
  { id: "yt-les-vid-os-d-alexis-sur-", nom: "Les vidéos d'Alexis sur le no-code et l'IA", famille: "Vidéos FR", type: "yt", canal: "UCm7-5hDaDYnktvIKj-_3Dsg", poids: 0.9, abo: true },
  { id: "yt-defend-intelligence", nom: "Defend Intelligence", famille: "Vidéos FR", type: "yt", canal: "UCnEHCrot2HkySxMTmDPhZyg", poids: 0.9, abo: true },
  { id: "yt-ai-impact", nom: "AI Impact", famille: "Vidéos FR", type: "yt", canal: "UCnNA2EuEVybpo3WGEace4HQ", poids: 0.9, abo: true },
  { id: "yt-parlons-ia-tech", nom: "Parlons IA & Tech", famille: "Vidéos FR", type: "yt", canal: "UCrRlS6QE1DsKnLDksvaBkKA", poids: 0.9, abo: true },
  { id: "yt-hyperbolic-ai", nom: "Hyperbolic AI", famille: "Vidéos FR", type: "yt", canal: "UCrS0xtNJz7sKoNoMyWeu3vQ", poids: 0.9, abo: true },
  { id: "yt-john-savage-ai", nom: "John Savage AI", famille: "Vidéos EN", type: "yt", canal: "UCwTOdeFTxWugbVQY9c-n41Q", poids: 0.9, abo: true },
  { id: "yt-jack-roberts", nom: "Jack Roberts", famille: "Vidéos EN", type: "yt", canal: "UCxVxcTULO9cFU6SB9qVaisQ", poids: 0.9, abo: true },
  { id: "yt-henri-exploria", nom: "Henri · ExplorIA", famille: "Vidéos FR", type: "yt", canal: "UCxx03UqvjTy9w8iomLwTSuQ", poids: 0.9, abo: true },
  { id: "yt-baptiste-simard-ia", nom: "Baptiste Simard - IA", famille: "Vidéos FR", type: "yt", canal: "UCzabGLybo9x307MkDtqTyFQ", poids: 0.9, abo: true },
  { id: "yt-ia-boss", nom: "IA Boss", famille: "Vidéos FR", type: "yt", canal: "UCzfBpdMdcuc6vyIvnprz3KQ", poids: 0.9, abo: true },
  { id: "yt-ia-360", nom: "IA 360°", famille: "Vidéos FR", type: "yt", canal: "UCzuBg7CyVW_K-PDq1l9YQ-g", poids: 0.9, abo: true },
];

// Dépôts GitHub : mots qui signalent un projet IA
export const MOTS_DEPOT = /\b(ai|llm|llms|gpt|agent|agents|agentic|mcp|rag|claude|codex|cursor|copilot|gemini|openai|anthropic|ollama|llama|qwen|deepseek|mistral|whisper|tts|stt|asr|voice|diffusion|comfy|comfyui|lora|gguf|vllm|inference|embedding|vector|transformer|neural|model|models|vision|vlm|multimodal|chatbot|prompt|automation|browser-use|computer-use|robot|robotics|3d|video|image)\b/i;

// Types de modèles Hugging Face → libellé français
export const TYPES_MODELE = {
  "text-generation": "Texte", "image-text-to-text": "Vision", "text-to-image": "Image", "image-to-image": "Retouche d'image",
  "text-to-video": "Vidéo", "image-to-video": "Vidéo", "video-text-to-text": "Vidéo → texte", "text-to-speech": "Voix",
  "text-to-audio": "Audio / musique", "automatic-speech-recognition": "Transcription", "audio-text-to-text": "Audio → texte",
  "translation": "Traduction", "any-to-any": "Multimodal", "feature-extraction": "Recherche (embeddings)", "sentence-similarity": "Recherche (embeddings)",
  "text-to-3d": "3D", "image-to-3d": "3D", "object-detection": "Vision", "image-segmentation": "Vision", "depth-estimation": "Vision",
  "robotics": "Robotique", "reinforcement-learning": "Robotique", "text-ranking": "Recherche (embeddings)", "audio-to-audio": "Audio / musique",
};

export const MOTS_IA = /\b(ia|i\.a\.|intelligence artificielle|ai|a\.i\.|llm|llms|gpt|chatgpt|openai|anthropic|claude|gemini|mistral|llama|deepseek|qwen|copilot|agent|agents|agentique|modèle de langage|language model|machine learning|apprentissage automatique|neural|neuronal|diffusion|transformer|nvidia|gpu|npu|inférence|inference|robot|robotique|hugging ?face|ollama|perplexity|grok|xai|midjourney|sora)\b/i;

// Thèmes de l'édition (ordre d'affichage) — le premier bloc « Le plus important » est calculé à part
export const RUBRIQUES = [
  { id: "modeles", titre: "Modèles" },
  { id: "idees", titre: "Idées et outils" },
  { id: "local", titre: "IA locale et matériel" },
  { id: "recherche", titre: "Recherche et monde" },
];

// Poids de départ des thèmes (priorité forte du cahier : modèles, local/matériel, agents/outils)
export const POIDS_RUBRIQUES = { modeles: 1.3, idees: 1.2, local: 1.3, recherche: 1.0 };
