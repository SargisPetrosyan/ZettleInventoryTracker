from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import JSONResponse

app = FastAPI()


@app.post("/zettle-webhook",)
async def zettle_webhook(request:Request):
    try:
        payload = await request.json()
        print("Received Zettle event:", payload)
        # TODO: process the event here (e.g., payment.paid)
        return JSONResponse(content={"status": "ok"})
    except Exception as e:
        print("Error processing webhook:", e)
        raise HTTPException(status_code=400, detail="Invalid payload")