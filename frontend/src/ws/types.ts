/**
 * WebSocket event type definitions for FedSentinel X.
 */
export type EventBase = {
  event_id: string;
  event_type: string;
  round_id?: string;
  update_id?: string;
  hospital_id?: string;
  timestamp: string; // ISO8601
  sequence?: number;
  payload?: Record<string, unknown>;
};

export type RoundEvent = EventBase & {
  event_type: 'ROUND_CREATED' | 'ROUND_STARTED' | 'ROUND_COMPLETED' | 'ROUND_FAILED' | 'ROUND_CLOSED';
  payload: {
    status: string;
    name?: string;
  };
};

export type HospitalEvent = EventBase & {
  event_type: 'HOSPITAL_CONNECTED' | 'HOSPITAL_TRAINING' | 'HOSPITAL_JOINED' | 'HOSPITAL_LEFT';
  payload: {
    online: boolean;
    trust_level?: number;
  };
};

export type UpdateEvent = EventBase & {
  event_type: 'UPDATE_CREATED' | 'UPDATE_SUBMITTED' | 'UPDATE_QUARANTINED' | 'UPDATE_ACCEPTED' | 'UPDATE_REJECTED';
  payload: {
    status: string;
    metrics?: Record<string, unknown>;
  };
};

export type SecurityStageEvent = EventBase & {
  event_type:
    | 'L0_STARTED'
    | 'L0_COMPLETED'
    | 'L1_STARTED'
    | 'L1_COMPLETED'
    | 'L2_STARTED'
    | 'L2_COMPLETED'
    | 'L3_STARTED'
    | 'L3_COMPLETED'
    | 'L4_STARTED'
    | 'L4_COMPLETED'
    | 'L5_STARTED'
    | 'L5_COMPLETED';
  payload: {
    status: 'PENDING' | 'RUNNING' | 'PASSED' | 'FAILED' | 'ANOMALOUS';
    reason?: string;
  };
};

export type TrustDecisionEvent = EventBase & {
  event_type: 'TRUST_EVALUATION_STARTED' | 'TRUST_DECISION_CREATED';
  payload: {
    decision: 'ACCEPT' | 'REJECT' | 'QUARANTINE';
    confidence?: number;
  };
};

export type AggregationEvent = EventBase & {
  event_type: 'AGGREGATION_STARTED' | 'AGGREGATION_COMPLETED';
  payload: {
    model_version: string;
  };
};

export type IncidentEvent = EventBase & {
  event_type: 'INCIDENT_CREATED' | 'INCIDENT_UPDATED';
  payload: {
    severity: 'LOW' | 'MEDIUM' | 'HIGH' | 'CRITICAL';
    status: string;
    reason?: string;
  };
};

export type AnyFedSentinelEvent =
  | RoundEvent
  | HospitalEvent
  | UpdateEvent
  | SecurityStageEvent
  | TrustDecisionEvent
  | AggregationEvent
  | IncidentEvent;
