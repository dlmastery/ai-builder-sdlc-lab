# product · password reset

**Signal:** customer test 2 (2026-09-09, chapter 17, confusing 16): a wrong password shows "invalid email or password" and there is no way back in without asking someone.

**What is missing:** a "forgot password" path — a reset token sent to the work email, a page that accepts it, an audit row for the change. Needs an outbound email route, which the product does not have (the only outbound call today is the payment provider's test mode).

**Constraint carried over:** nothing leaves the network without the AI Builder's say; an email route is a new outbound call and must be listed on the security facts before it ships.

**Triage:** a human decides whether this enters the next loop's plan.
