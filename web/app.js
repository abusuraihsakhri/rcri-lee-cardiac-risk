// Client-side RCRI. All calculations remain in this browser tab.
export const FACTORS = Object.freeze([
  "high_risk_surgery",
  "ischemic_heart_disease",
  "heart_failure",
  "cerebrovascular_disease",
  "insulin_treatment",
  "creatinine_ge_2"
]);
const RATES = [0.4, 0.9, 7.0, 11.0];
const CLASSES = ["Class I", "Class II", "Class III", "Class IV"];

export function calculateRcri(values) {
  if (!values || typeof values !== "object" ||
      Object.keys(values).length !== FACTORS.length ||
      Object.keys(values).some(key => !FACTORS.includes(key))) {
    throw new TypeError("Exactly six RCRI predictors are required");
  }
  for (const key of FACTORS) {
    if (typeof values[key] !== "boolean") {
      throw new TypeError(key + " must be true or false");
    }
  }
  const score = FACTORS.filter(key => values[key]).length;
  const category = Math.min(score, 3);
  return {
    score,
    classification: CLASSES[category],
    riskCategory: score >= 2 ? "Elevated" : "Low",
    validationRate: RATES[category]
  };
}

if (typeof document !== "undefined") {
  const form = document.querySelector("#rcri-form");
  const reset = document.querySelector("#reset-form");
  const scoreValue = document.querySelector("#score");
  const riskValue = document.querySelector("#risk");
  const rateValue = document.querySelector("#rate");
  const categoryValue = document.querySelector("#class");
  const details = document.querySelector("#details");

  function update() {
    const values = Object.fromEntries(FACTORS.map(key => [
      key, form.elements.namedItem(key).checked
    ]));
    const result = calculateRcri(values);
    scoreValue.textContent = String(result.score);
    categoryValue.textContent = result.classification;
    riskValue.textContent = result.riskCategory + " perioperative risk category";
    rateValue.textContent = result.validationRate.toFixed(1) + "%";
    const active = FACTORS.filter(key => values[key]);
    details.textContent = active.length
      ? active.length + " predictor" + (active.length === 1 ? "" : "s") + " present"
      : "No predictors selected";
  }
  form.addEventListener("change", update);
  reset.addEventListener("click", () => {
    form.reset();
    update();
    form.querySelector("input").focus();
  });
  update();
}
