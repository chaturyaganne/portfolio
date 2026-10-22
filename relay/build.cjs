const fs=require('node:fs'),path=require('node:path');
const out=path.join(__dirname,'dist');fs.mkdirSync(out,{recursive:true});
const data=JSON.parse(fs.readFileSync(path.join(__dirname,'data.json'),'utf8'));
fs.writeFileSync(path.join(out,'data.js'),'window.RelayData='+JSON.stringify(data)+';\n');
for(const file of ['index.html','site.css','app.js','core.js','data.json','server.cjs','package.json','README.md','tests.cjs','build.cjs'])fs.copyFileSync(path.join(__dirname,file),path.join(out,file));
console.log('Built standalone Relay website and source in dist/.');
