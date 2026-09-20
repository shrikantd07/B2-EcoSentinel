# EcoSentinel Live Demo Checklist

## Start the backend

From the repository root:

```powershell
python -m uvicorn backend.app.main:app --host 127.0.0.1 --port 8000
```

Verify `http://127.0.0.1:8000/health` returns HTTP 200.

## Start the frontend

In a second terminal:

```powershell
cd frontend
npm run dev -- --host localhost
```

Open `http://localhost:5173`. Vite is configured with `strictPort: true`; if port 5173 is occupied, stop the old frontend process instead of changing the port.

## Demo flow

1. Confirm the default form values are visible.
2. Submit the default form without an image.
3. Confirm the report displays the overall risk, coordinator reasoning, specialist cards, and recommended actions.
4. Confirm the RAG guidance card displays retrieved environmental guidance.
5. Upload a JPEG, PNG, or WEBP image under 5 MB.
6. Confirm the image preview appears, submit again, and confirm image-analysis details appear in the waste card.
7. Confirm an invalid file type or oversized image produces a visible validation error.

## API smoke checks

```powershell
Invoke-RestMethod http://127.0.0.1:8000/health
```

The no-image form submits to `POST /api/analyze`; an image submission uses `POST /api/analyze-image`.

## Quality checks

```powershell
cd frontend
npm run lint
npm run build
```

Run `pip check` in the active Python environment when dependency verification is required.

## Known local-environment considerations

- The backend API is configured for `127.0.0.1:8000`.
- The frontend is configured for `localhost:5173` and must not silently move to another port.
- Do not commit `.venv`, `node_modules`, build output, ZIP snapshots, or secrets.
- Browser click-through was not automated in this repository environment; perform the visual flow manually during the live demo.
