import React, {useState} from 'react';

export default function App(){
  const [role,setRole] = useState("");
  const [level,setLevel] = useState("mid");
  const [jobDescription,setJobDescription] = useState("");
  const [myExperience,setMyExperience] = useState("");
  const [res,setRes] = useState(null);
  const [loading,setLoading] = useState(false);

  async function submit(e){
    e.preventDefault();
    setLoading(true);
    setRes(null);
    const payload = {
      role,
      level,
      job_description: jobDescription,
      my_experience: myExperience
    };
    const r = await fetch("/predict", {
      method: "POST",
      headers: {"Content-Type":"application/json"},
      body: JSON.stringify(payload)
    });
    const j = await r.json();
    setRes(JSON.stringify(j.raw, null, 2));
    setLoading(false);
  }

  return (<div style={{maxWidth:900, margin:"40px auto", fontFamily:"sans-serif"}}>
    <h2>Job Interview Agent (JD-based)</h2>
    <form onSubmit={submit}>
      <div>
        <label>Role</label><br/>
        <input value={role} onChange={e=>setRole(e.target.value)} style={{width:"100%"}} required/>
      </div>
      <div style={{marginTop:8}}>
        <label>Level</label><br/>
        <select value={level} onChange={e=>setLevel(e.target.value)}>
          <option value="junior">junior</option>
          <option value="mid">mid</option>
          <option value="senior">senior</option>
        </select>
      </div>
      <div style={{marginTop:8}}>
        <label>Job Description / Role Context</label><br/>
        <textarea value={jobDescription} onChange={e=>setJobDescription(e.target.value)} rows={6} style={{width:"100%"}} placeholder="Paste JD or role context here"/>
      </div>
      <div style={{marginTop:8}}>
        <label>My Experience / Resume Highlights</label><br/>
        <textarea value={myExperience} onChange={e=>setMyExperience(e.target.value)} rows={6} style={{width:"100%"}} placeholder="Summarize your experience, skills, achievements"/>
      </div>
      <div style={{marginTop:12}}>
        <button type="submit" disabled={loading}>{loading?"Generating...":"Generate Questions & Prep"}</button>
      </div>
    </form>
    <pre style={{whiteSpace:"pre-wrap", marginTop:20, background:"#f6f6f6", padding:12}}>{res||"Results will appear here"}</pre>
  </div>);
}

