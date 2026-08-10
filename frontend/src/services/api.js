const BASE = import.meta.env.VITE_API_BASE || "http://localhost:8000";
export async function api(path, options={}) {
  const token=localStorage.getItem("nexo_token");
  const response=await fetch(BASE+path,{...options,headers:{"Content-Type":"application/json",...(token?{Authorization:`Bearer ${token}`}:{}) ,...(options.headers||{})}});
  const data=await response.json().catch(()=>({message:"Invalid server response"}));
  if(!response.ok) throw new Error(data.message||data.detail||"Request failed");
  return data;
}
export {BASE};
