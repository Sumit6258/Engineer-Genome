import strawberry
from strawberry.types import Info
from typing import Optional

from app.api.types.resume import ResumeJob, db_job_to_graphql


@strawberry.type
class Query:
    @strawberry.field(description="Poll a resume job for its current status and results.")
    async def resume_job(self, job_id: str, info: Info) -> Optional[ResumeJob]:
        """
        The client calls this repeatedly after uploading a resume.

        Typical polling pattern:
          1. Client uploads resume → gets job_id
          2. Client calls resumeJob(jobId: "...") every 2 seconds
          3. When status is COMPLETED, show the results
          4. When status is FAILED, show the error

        In production you would replace polling with GraphQL Subscriptions
        (Phase 7) so the server pushes the update when ready.
        """
        service = info.context["resume_service"]
        job = await service.get_job(job_id)
        if not job:
            return None
        return db_job_to_graphql(job)

    @strawberry.field(description="Get all resume jobs for a user, most recent first.")
    async def user_resume_jobs(
        self,
        username: str,
        info: Info,
        limit: int = 10,
    ) -> list[ResumeJob]:
        service = info.context["resume_service"]
        jobs = await service.get_user_jobs(username, limit)
        return [db_job_to_graphql(j) for j in jobs]
