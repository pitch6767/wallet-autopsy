async () => {
  const moduleCode = __REALISM_MODULE__;
  const base = "/accounts/0ed933adade0cc382cc2334fadefd457/workers/scripts/bot95";
  const [script, settingsResponse, deployments] = await Promise.all([
    cloudflare.request({method:"GET",path:base}),
    cloudflare.request({method:"GET",path:base+"/settings"}),
    cloudflare.request({method:"GET",path:base+"/deployments",query:{per_page:1}}),
  ]);
  if(!script.success||!settingsResponse.success||!deployments.success)throw Error("Cannot capture current deployment");
  const settings=settingsResponse.result;
  if(settings.bindings.some(b=>b.name==="REALISM"))throw Error("REALISM already exists; review before updating");
  const raw=script.result;
  const parts=[...raw.matchAll(/Content-Disposition: form-data; name="([^"]+)"/g)];
  if(parts.length!==1||parts[0][1]!=="index.js")throw Error("Unexpected module layout");
  const begin=raw.indexOf("\r\n\r\n")+4;
  const end=raw.lastIndexOf("\r\n--");
  if(begin<4||end<begin)throw Error("Invalid multipart source");
  let source=raw.slice(begin,end);
  const needle="  async fetch(req, env) {\n    return stub(env).fetch(req);\n  },";
  if(source.split(needle).length!==2)throw Error("Routing anchor not unique");
  source=source.replace(needle,`  async fetch(req, env) {
    const path = new URL(req.url).pathname;
    if(path === "/rapide-realiste" || path.startsWith("/api/realism/"))
      return env.REALISM.get(env.REALISM.idFromName("maker-realism")).fetch(req);
    const response = await stub(env).fetch(req);
    if(req.method === "GET" && response.status === 200 &&
       (response.headers.get("content-type") || "").includes("text/html")) {
      return new HTMLRewriter().on("body", {element(e) {
        e.prepend('<nav style="padding:12px;background:#e9f2ff"><a href="/rapide-realiste">Bot95 — résultats maker corrigés et bilan 24 h</a></nav>', {html:true});
      }}).transform(response);
    }
    return response;
  },`);
  source='import { RealismStore } from "./realism.mjs";\n'+source+'\nexport { RealismStore };\n';
  const metadata={
    main_module:"index.js",
    compatibility_date:settings.compatibility_date,
    compatibility_flags:settings.compatibility_flags,
    bindings:[...settings.bindings.map(b=>({name:b.name,type:"inherit"})),
      {name:"REALISM",type:"durable_object_namespace",class_name:"RealismStore"}],
    migrations:{old_tag:"v2",new_tag:"maker-realism-20261012",new_sqlite_classes:["RealismStore"]},
    keep_assets:true,
    annotations:{"workers/message":"Isolated Bot95 maker realism dashboard; existing trading settings unchanged"},
  };
  for(const key of ["usage_model","limits","logpush","tail_consumers","tags","observability"])
    if(settings[key]!==undefined)metadata[key]=settings[key];
  const boundary="bot95-realism-"+Date.now();
  const body=[
    "--"+boundary,'Content-Disposition: form-data; name="metadata"',"Content-Type: application/json","",JSON.stringify(metadata),
    "--"+boundary,'Content-Disposition: form-data; name="index.js"; filename="index.js"',"Content-Type: application/javascript+module","",source,
    "--"+boundary,'Content-Disposition: form-data; name="realism.mjs"; filename="realism.mjs"',"Content-Type: application/javascript+module","",moduleCode,
    "--"+boundary+"--","",
  ].join("\r\n");
  const response=await cloudflare.request({method:"PUT",path:base,body,rawBody:true,contentType:"multipart/form-data; boundary="+boundary});
  if(!response.success)return {success:false,status:response.status,errors:response.errors};
  const after=await cloudflare.request({method:"GET",path:base+"/settings"});
  const unchanged=settings.bindings.every(b=>JSON.stringify(b)===JSON.stringify(after.result.bindings.find(x=>x.name===b.name)));
  return {success:true,previousDeployments:deployments.result?.deployments?.map(x=>({id:x.id,versions:x.versions})),
    existingBindingsUnchanged:unchanged,newBinding:after.result.bindings.find(x=>x.name==="REALISM"),
    version:response.result?.deployment_id,errors:response.errors};
}
