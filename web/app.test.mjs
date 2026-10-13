import test from "node:test";
import assert from "node:assert/strict";
import { FACTORS, calculateRcri } from "./app.js";

test("scores all 64 Boolean configurations", () => {
  for (let mask = 0; mask < 64; mask++) {
    const values = Object.fromEntries(FACTORS.map((name, i) => [name, Boolean(mask & (1 << i))]));
    const score = FACTORS.filter(name => values[name]).length;
    const result = calculateRcri(values);
    assert.equal(result.score, score);
    assert.equal(result.classification, ["Class I", "Class II", "Class III", "Class IV"][Math.min(3, score)]);
    assert.equal(result.validationRate, [0.4, 0.9, 7.0, 11.0][Math.min(3, score)]);
    assert.equal(result.riskCategory, score >= 2 ? "Elevated" : "Low");
  }
});

test("rejects missing or malformed predictor values", () => {
  assert.throws(() => calculateRcri({}), TypeError);
  assert.throws(() => calculateRcri(null), TypeError);
  const values = Object.fromEntries(FACTORS.map(key => [key, false]));
  assert.throws(() => calculateRcri({ ...values, heart_failure: "false" }), TypeError);
  assert.throws(() => calculateRcri({ ...values, extra: true }), TypeError);
});
