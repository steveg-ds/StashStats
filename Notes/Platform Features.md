**Ravelry is a comprehensive social networking and organizational platform specifically designed for knitters, crocheters, designers, spinners, weavers, and dyers**. Because the company does not develop its own official native mobile applications for iOS or Android, it heavily relies on its API to expose its core platform features to third-party developers, allowing them to build a vibrant ecosystem of mobile apps, web integrations, and data research tools.

The sources highlight several major platform features that are accessible and manageable through the Ravelry API:

### 1. The Global Database of Patterns and Yarns

At the foundation of Ravelry is its massive, community-driven database. As of data referenced from 2014–2015, the platform hosted approximately 300,000 knitting patterns, over 9 million project pages, and served 5 million users.

- **Pattern Discovery:** The API enables complex querying of the pattern database, allowing users to filter by craft type, availability (e.g., free or paid), and fit. It exposes highly detailed, nested attributes for each pattern, including the community's difficulty average, stockinette stitch gauge density, recommended needle sizes, and specific yardage or yarn requirements.
- **Material Classification:** Ravelry acts as an exhaustive index for materials. The API provides standardized endpoints to retrieve standard metric yarn weights (thicknesses), fiber categories, and standard dye/color families.
- **Designers and Sources:** Users can explore pattern authors, view their featured pattern bundles, and search through pattern sources like books, booklets, and magazines.

### 2. "The Notebook" (Personal Organizational Tools)

A central feature of Ravelry is the user "Notebook," which acts as a personal database for individual crafters. Using OAuth or basic authentication, the API allows external applications to interact securely with these personal records.

- **Projects:** Users can create and manage project pages to document their progress. Projects can be linked directly to specific patterns and yarns, and users can add personal notes, track completion dates, specify the needles/hooks used, and upload project photos directly from third-party mobile apps.
- **Yarn Stash:** Crafters can track their personal inventory of yarn and fiber. Stash entries include detailed attributes like the yarn company, dye lot, color family, weight, and quantity of skeins owned. Users can also upload photos of their stash directly from their device cameras.
- **Queues:** Users can plan future crafting endeavors by adding patterns to a queue. The API allows apps to reposition queued projects and track the expected yarn required for them.
- **Favorites and Bundles:** Crafters can bookmark their favorite patterns, yarns, designers, or forum posts. These bookmarks can be logically grouped into specialized "bundles".
- **Library:** The platform allows users to maintain a digital library of their owned pattern books, magazines, and individual PDFs.

### 3. Community and Social Networking

As a social network, Ravelry provides robust tools for interaction, which are mirrored in the API.

- **Forums:** The API supports reading, posting, and replying to community forum threads. It also features a unique voting mechanism where users can react to forum posts by rating them with specific tags: _interesting_, _educational_, _funny_, _agree_, _disagree_, or _love_.
- **Direct Messaging:** Ravelry facilitates private communication, allowing users to create, read, reply to, archive, and delete direct messages.
- **Friends and Activity Feeds:** Users can add friends and subscribe to their activity feeds. This feature streams updates when a friend favorites an item, queues a pattern, or adds new photos to a project or stash.

### 4. Commerce and Retail Integrations

Ravelry bridges the gap between independent digital designers, physical yarn stores, and crafters.

- **Shop Locator:** The API includes geographic search capabilities using latitude, longitude, and radius to locate physical yarn shops. This feature specifically allows developers to filter for "Local Yarn Stores" (LYS) to exclude large corporate craft chains.
- **Shopping Carts and Checkout:** External pattern stores can use the API to manage shopping carts and process external checkouts. Once a transaction is verified, Ravelry generates an invoice and securely delivers the digital PDFs directly to the customer's library.
- **In-Store Sales Program:** This program allows brick-and-mortar retail shops to act as digital pattern vendors. Stores can process a pattern purchase at the register on behalf of a customer; the wholesale price is subsequently added to the store's monthly Ravelry bill, and the digital pattern is emailed or sent to the customer's Ravelry account.

### 5. Third-Party "Goodies" and Mobile Applications

Because Ravelry focuses its internal resources entirely on its website, the API is the engine behind all mobile experiences.

- **Mobile Apps:** Developers have built numerous third-party apps—such as Wooly, Stitch, Ravulous, and KnitKapp—that utilize the API to give users pocket-access to their stash, queue, and patterns, as well as the ability to upload photos directly from a phone's camera.
- **Web Integration Tools:** The platform provides embeddable "goodies" for external blogs and websites. This includes progress bars to display project status, project counter buttons for designers' websites, and browser bookmarklets (like "Ravel It") that allow users to quickly jump from an external pattern website to its corresponding Ravelry entry.