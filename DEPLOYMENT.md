# Deploy BIS Sahayak for teammates

This project deploys as two services:

1. **Render** hosts the FastAPI backend.
2. **Vercel** hosts the Next.js frontend.

The backend must deploy first because Vercel needs its public URL.

## Before you begin

1. Create free accounts at [GitHub](https://github.com), [Render](https://render.com), and [Vercel](https://vercel.com).
2. Create a new GitHub repository, for example `bis-sahayak`.
3. Upload the complete project folder to that repository. Keep `frontend`, `backend`, and `render.yaml` together at the repository root.

Do not upload `.venv`, `node_modules`, `.next`, or any file containing keys or passwords.

## Upload the project to GitHub

After creating an empty GitHub repository, open PowerShell in this project folder and run:

```powershell
git init
git add .
git commit -m "Prepare BIS Sahayak deployment"
git branch -M main
git remote add origin https://github.com/YOUR-USERNAME/bis-sahayak.git
git push -u origin main
```

Replace `YOUR-USERNAME` with your GitHub username. If Git asks for your name and email before the commit, run:

```powershell
git config --global user.name "Your Name"
git config --global user.email "your-email@example.com"
```

## 1. Deploy the backend on Render

1. In Render, select **New** and then **Blueprint**.
2. Connect GitHub and select the `bis-sahayak` repository.
3. Render reads `render.yaml`. Review the detected `bis-sahayak-api` web service and create it.
4. Wait for the deploy to finish. Render gives you a public URL such as:

   ```text
   https://bis-sahayak-api.onrender.com
   ```

5. Open this address with `/health` added to the end:

   ```text
   https://bis-sahayak-api.onrender.com/health
   ```

   It should return a JSON response with `"status": "ok"`.

## 2. Deploy the frontend on Vercel

1. In Vercel, select **Add New** and then **Project**.
2. Import the same GitHub repository.
3. In the import settings, set **Root Directory** to `frontend`.
4. Open **Environment Variables** and add:

   | Name | Value |
   | --- | --- |
   | `NEXT_PUBLIC_API_BASE_URL` | Your Render URL, for example `https://bis-sahayak-api.onrender.com` |

   Do not add a slash at the end of the URL.

5. Click **Deploy**. Vercel gives you a URL such as:

   ```text
   https://bis-sahayak.vercel.app
   ```

## 3. Allow the deployed frontend in Render

1. Return to the `bis-sahayak-api` service in Render.
2. Open **Environment**.
3. Change `CORS_ORIGINS` from `http://localhost:3000` to your Vercel URL, for example:

   ```text
   https://bis-sahayak.vercel.app
   ```

4. Save the change and redeploy the service.

This lets the browser call the backend only from your deployed frontend. If you add a custom domain later, append it with a comma:

```text
https://bis-sahayak.vercel.app,https://your-domain.example
```

## 4. Final check

Open the Vercel URL in an incognito/private browser window. Enter a product query, for example:

```text
I manufacture laptops and want to understand BIS readiness.
```

Select **Build my readiness roadmap**. The analysis page should load BIS sources and the roadmap without a browser error.

## Updating the app

Push changes to the connected GitHub branch. Render redeploys the backend and Vercel redeploys the frontend automatically.

## Important limits

- This prototype stores only the bundled BIS source corpus. It does not require PostgreSQL or a database to deploy.
- Uploaded PDFs are processed by the running backend and are not intentionally saved by the code.
- The deployed application remains a readiness-guidance prototype, not a BIS certification system.
