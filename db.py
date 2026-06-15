from supabase import create_client
from config import SUPABASE_URL, SUPABASE_KEY

supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

# ─── Users ───────────────────────────────────────────
def get_user(user_id: int):
    res = supabase.table("users").select("*").eq("id", user_id).execute()
    return res.data[0] if res.data else None

def create_user(user_id: int, username: str, full_name: str, role: str, skills=None, bio=""):
    data = {
        "id": user_id,
        "username": username,
        "full_name": full_name,
        "role": role,
        "skills": skills or [],
        "bio": bio,
    }
    return supabase.table("users").insert(data).execute()

# ─── Projects ────────────────────────────────────────
def create_project(employer_id, title, description, budget_min, budget_max, deadline_days):
    data = {
        "employer_id": employer_id,
        "title": title,
        "description": description,
        "budget_min": budget_min,
        "budget_max": budget_max,
        "deadline_days": deadline_days,
    }
    res = supabase.table("projects").insert(data).execute()
    return res.data[0] if res.data else None

def get_open_projects():
    res = supabase.table("projects").select("*, users(full_name)").eq("status", "open").order("created_at", desc=True).execute()
    return res.data

def get_project(project_id: str):
    res = supabase.table("projects").select("*, users(full_name)").eq("id", project_id).execute()
    return res.data[0] if res.data else None

def update_project_status(project_id: str, status: str, freelancer_id=None):
    data = {"status": status}
    if freelancer_id:
        data["selected_freelancer_id"] = freelancer_id
    supabase.table("projects").update(data).eq("id", project_id).execute()

# ─── Proposals ───────────────────────────────────────
def create_proposal(project_id, freelancer_id, price, delivery_days, description):
    data = {
        "project_id": project_id,
        "freelancer_id": freelancer_id,
        "price": price,
        "delivery_days": delivery_days,
        "description": description,
    }
    res = supabase.table("proposals").insert(data).execute()
    return res.data[0] if res.data else None

def get_project_proposals(project_id: str):
    res = supabase.table("proposals").select("*, users(full_name, rating, rating_count)").eq("project_id", project_id).execute()
    return res.data

def get_proposal(proposal_id: str):
    res = supabase.table("proposals").select("*").eq("id", proposal_id).execute()
    return res.data[0] if res.data else None

def update_proposal_status(proposal_id: str, status: str):
    supabase.table("proposals").update({"status": status}).eq("id", proposal_id).execute()

def get_freelancer_proposals(freelancer_id: int):
    res = supabase.table("proposals").select("*, projects(title, status)").eq("freelancer_id", freelancer_id).execute()
    return res.data

# ─── Messages ────────────────────────────────────────
def save_message(project_id, sender_id, receiver_id, content):
    data = {
        "project_id": project_id,
        "sender_id": sender_id,
        "receiver_id": receiver_id,
        "content": content,
    }
    supabase.table("messages").insert(data).execute()

def get_project_messages(project_id: str):
    res = supabase.table("messages").select("*").eq("project_id", project_id).order("created_at").execute()
    return res.data

# ─── Escrow ──────────────────────────────────────────
def create_escrow(project_id, amount, payment_ref):
    data = {"project_id": project_id, "amount": amount, "payment_ref": payment_ref}
    supabase.table("escrow").insert(data).execute()

def get_escrow(project_id: str):
    res = supabase.table("escrow").select("*").eq("project_id", project_id).execute()
    return res.data[0] if res.data else None

def update_escrow_status(project_id: str, status: str):
    supabase.table("escrow").update({"status": status}).eq("project_id", project_id).execute()

# ─── Ratings ─────────────────────────────────────────
def create_rating(project_id, rater_id, rated_id, score, comment):
    data = {
        "project_id": project_id,
        "rater_id": rater_id,
        "rated_id": rated_id,
        "score": score,
        "comment": comment,
    }
    supabase.table("ratings").insert(data).execute()
    # update average rating
    res = supabase.table("ratings").select("score").eq("rated_id", rated_id).execute()
    scores = [r["score"] for r in res.data]
    avg = sum(scores) / len(scores)
    supabase.table("users").update({"rating": round(avg, 2), "rating_count": len(scores)}).eq("id", rated_id).execute()
