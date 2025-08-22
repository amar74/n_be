// functions/new-user-webhook/index.ts
import "jsr:@supabase/functions-js/edge-runtime.d.ts";
console.info("Edge function started");
Deno.serve(async (req)=>{
  try {
    // Ensure it’s a POST request
    if (req.method !== "POST") {
      return new Response("Method not allowed", {
        status: 405
      });
    }
    const payload = await req.json();
    const user = payload?.record;
    if (!user) {
      return new Response("Invalid payload", {
        status: 400
      });
    }
    // Specify the URL to send the new user data to
    // const webhookUrl = "https://enough-llama-optimal.ngrok-free.app/auth/onsignup";
    const webhookUrl = "https://13a3717dffb2.ngrok-free.app/auth/onsignup";
    // Forward the user data to your external API/webhook
    const webhookRes = await fetch(webhookUrl, {
      method: "POST",
      headers: {
        "Content-Type": "application/json"
      },
      body: JSON.stringify({
        id: user.id,
        email: user.email,
        created_at: user.created_at
      })
    });
    if (!webhookRes.ok) {
      console.error("Failed to send to webhook", await webhookRes.text());
      return new Response("Webhook failed", {
        status: 500
      });
    }
    return new Response("User data sent successfully", {
      status: 200
    });
  } catch (error) {
    console.error("Error handling request", error);
    return new Response("Internal Server Error", {
      status: 500
    });
  }
});
