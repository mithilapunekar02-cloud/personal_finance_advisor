function openModal(id){document.getElementById(id).classList.add("show")}
function closeModal(id){document.getElementById(id).classList.remove("show")}

const txForm = document.getElementById("transactionForm");
if(txForm){
  txForm.addEventListener("submit", async (e)=>{
    e.preventDefault();
    const data = Object.fromEntries(new FormData(txForm));
    data.amount = Number(data.amount);
    const r = await fetch("/api/transaction",{method:"POST",headers:{"Content-Type":"application/json"},body:JSON.stringify(data)});
    if(r.ok) location.reload(); else alert("Could not save transaction.");
  });
}
const budgetForm = document.getElementById("budgetForm");
if(budgetForm){
  budgetForm.addEventListener("submit", async (e)=>{
    e.preventDefault();
    const data = Object.fromEntries(new FormData(budgetForm));
    data.amount = Number(data.amount);
    const r = await fetch("/api/budget",{method:"POST",headers:{"Content-Type":"application/json"},body:JSON.stringify(data)});
    if(r.ok) location.reload(); else alert("Could not save budget.");
  });
}
async function getAdvice(){
  const box = document.getElementById("advice");
  box.innerHTML = "Analyzing your finances…";
  const r = await fetch("/api/ai-advice",{method:"POST"});
  const data = await r.json();
  box.innerHTML = "<ul>" + data.advice.map(x=>`<li>${x}</li>`).join("") + "</ul><small>${data.note}</small>";
}
if(window.expenseData && document.getElementById("expenseChart")){
  const labels = Object.keys(window.expenseData);
  const values = Object.values(window.expenseData);
  new Chart(document.getElementById("expenseChart"),{
    type:"doughnut",
    data:{labels, datasets:[{data:values}]},
    options:{responsive:true,plugins:{legend:{position:"bottom",labels:{color:"#cdd4ce"}}}}
  });
}
