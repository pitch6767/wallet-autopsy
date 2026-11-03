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
  // GitHub
  { id: "trending", nom: "GitHub Trending", famille: "GitHub", type: "trending", url: "https://github.com/trending?since=daily", poids: 1.0 },
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
];

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
