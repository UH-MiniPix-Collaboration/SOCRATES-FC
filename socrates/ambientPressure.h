#define AMB_PRESSURE_PIN A0

float getAmbientPressure()
{
  float rawVal = analogRead(AMB_PRESSURE_PIN);
  rawVal = ((rawVal / 5) - 0.04) / 0.009;  // VOUT = VS (P x 0.009 + 0.04)
  return rawVal;
}
