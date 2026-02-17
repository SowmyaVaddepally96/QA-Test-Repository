p# BabyShop (Java) + Cypress (JavaScript)

Simple web application for shopping baby products: **browse**, **search**, **add to cart**, and **checkout**.

## Run the Java web app

Prereqs:
- Java 17+
- Maven 3.9+

From the repo root:

```bash
mvn spring-boot:run
```

Then open `http://localhost:8080`.

### Auto-open the browser (optional)

`mvn spring-boot:run` does **not** open your browser by default. To auto-open after startup:

```bash
mvn spring-boot:run -Dspring-boot.run.jvmArguments="-Dapp.open-browser=true"
```

Optional (change landing page):

```bash
mvn spring-boot:run -Dspring-boot.run.jvmArguments="-Dapp.open-browser=true -Dapp.open-browser-path=/products"
```

Notes:
- Uses **H2 in-memory database** seeded via `src/main/resources/data.sql`
- H2 console (optional): `http://localhost:8080/h2-console`

## Run Cypress tests (JavaScript)

Prereqs:
- Node 18+

Install dependencies:

```bash
npm install
```

With the Java app running on `http://localhost:8080`, run:

```bash
npm run cypress:run
```

Or interactive mode:

```bash
npm run cypress:open
```

## Login / Sign Up

- Navigate to `http://localhost:8080/auth`
- Login and Sign Up buttons are in the top nav beside Cart.

## Using “real” product images (important)

This repo currently uses **local demo SVG images** under `src/main/resources/static/images/` so the app works offline and without licensing risk.

If you want to use real photos:
- **Do not copy images from Google Images** unless you have explicit rights (most are copyrighted).
- Prefer **open-license** sources (e.g. Wikimedia Commons, Pexels, Pixabay) or **your own photos**.

How to replace images safely:
- Put your image files in `src/main/resources/static/images/` (e.g. `bottle-philips-avent.jpg`)
- Update `src/main/resources/data.sql` `image_url` values to point to `/images/<your-file>`
- Restart the app.

### Images used in the catalog

The catalog is currently configured to use **local images** from:

- `src/main/resources/static/images/`

Most filenames include spaces/apostrophes; `data.sql` uses URL-encoded `/images/...` paths so they load correctly in the browser.

A web application for shopping baby products, offering a user-friendly interface to browse, search, and purchase essentials for babies.
