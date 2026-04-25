import React, {useState} from 'react';

export default function App(){
  const [role,setRole] = useState("");
  const [level,setLevel] = useState("mid");
  const [res,setRes] = useState(null);
  const [loading,setLoading] = useState(false);

  async function submit(e){
    e.preventDefault();
    setLoading(true);
    setRes(null);
    try{
      const r = await fetch("/predict", {
        method: "POST",
        headers: {"Content-Type":"application/json"},
        body: JSON.stringify({role, level})
      });
      const j = await r.json();
      setRes(j.raw);
    }catch(err){
      setRes("Error: "+err.message);
    }finally{
      setLoading(false);
    }
  }

  return (<div style={{maxWidth:800, margin:"40px auto", fontFamily:"sans-serif"}}>
    <h2>Job Interview Agent (MVP)</h2>
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
      <div style={{marginTop:12}}>
        <button type="submit" disabled={loading}>{loading?"Generating...":"Generate Questions"}</button>
      </div>
    </form>
    <pre style={{whiteSpace:"pre-wrap", marginTop:20, background:"#f6f6f6", padding:12}}>{res||"Results will appear here"}</pre>
  </div>);
}
