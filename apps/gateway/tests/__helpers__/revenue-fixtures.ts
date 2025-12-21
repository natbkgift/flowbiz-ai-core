/**
 * Future intent: lightweight fixtures for Revenue Optimizer scenarios.
 * These shapes are intentionally minimal to keep the PR behavior-neutral.
 */

export type StreamMomentumState = "stable" | "spiking" | "cooldown";

export interface RevenueTestContext {
  audiencePersona: "work-hands" | "chatty" | "neutral";
  momentum: StreamMomentumState;
  channelProfile: "education" | "pk-heavy" | "variety";
  guardrailMode: "normal" | "panic" | "degraded";
}

export const baseContext: RevenueTestContext = {
  audiencePersona: "neutral",
  momentum: "stable",
  channelProfile: "variety",
  guardrailMode: "normal",
};

export const viewSpikeContext: RevenueTestContext = {
  ...baseContext,
  momentum: "spiking",
};

export const giftBurstContext: RevenueTestContext = {
  ...baseContext,
  momentum: "cooldown",
};

export const educationChannelContext: RevenueTestContext = {
  ...baseContext,
  channelProfile: "education",
};

export const pkHeavyChannelContext: RevenueTestContext = {
  ...baseContext,
  channelProfile: "pk-heavy",
};

export const panicGuardrailContext: RevenueTestContext = {
  ...baseContext,
  guardrailMode: "panic",
};

export const degradedGuardrailContext: RevenueTestContext = {
  ...baseContext,
  guardrailMode: "degraded",
};
