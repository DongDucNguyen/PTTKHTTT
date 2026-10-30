"""AssistantTurnDAO — Nhật ký trợ lý AI (kèm GroundingEvent)."""
from __future__ import annotations

from abc_fashion.control.dao.dao import DAO, _to_entity, _val
from abc_fashion.model.assistant import AssistantTurn, GroundingEvent
from abc_fashion.model.catalogue import Style
from abc_fashion.model.user import Customer


class AssistantTurnDAO(DAO):
    """Bảng tblAssistantTurn. Dùng bởi: AssistantFrm."""

    def add_assistant_turn(self, turn: AssistantTurn, customer: Customer | None, style: Style) -> bool:
        customer_id = customer.id if customer else None
        with self.con.transaction():
            row = self.con.execute(
                'INSERT INTO "tblAssistantTurn"("question","answer","mode","model_name","latency_ms","created_at",'
                '"customerId","styleId") VALUES (%s,%s,%s,%s,%s,now(),%s,%s) RETURNING "id","created_at"',
                ((turn.question or "")[:2000], (turn.answer or "")[:4000], _val(turn.mode), turn.model_name,
                 turn.latency_ms, customer_id, style.id if style else None)).fetchone()
            for e in getattr(turn, "grounding_events", []):
                e.id = self.con.execute(
                    'INSERT INTO "tblGroundingEvent"("check_name","removed_text","assistantTurnId") VALUES (%s,%s,%s) '
                    'RETURNING "id"', (_val(e.check_name), (e.removed_text or "")[:2000], row["id"])).fetchone()["id"]
                e.assistantTurnId = row["id"]
        turn.id, turn.created_at = row["id"], row["created_at"]
        turn.customerId, turn.styleId = customer_id, style.id if style else None
        return True

    def get_turn_by_customer(self, customer: Customer, style: Style) -> list[AssistantTurn]:
        rows = self.con.execute(
            'SELECT * FROM "tblAssistantTurn" WHERE "customerId" = %s AND "styleId" = %s ORDER BY "created_at", "id"',
            (customer.id, style.id)).fetchall()
        turns = [_to_entity(AssistantTurn, r) for r in rows]
        if turns:
            events = self.con.execute('SELECT * FROM "tblGroundingEvent" WHERE "assistantTurnId" = ANY(%s)',
                                      ([t.id for t in turns],)).fetchall()
            for t in turns:
                t.grounding_events = [_to_entity(GroundingEvent, e) for e in events if e["assistantTurnId"] == t.id]
        return turns
