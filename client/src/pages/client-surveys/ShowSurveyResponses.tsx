import { useFormbricks } from "@/hooks/use-formbricks";
import { useParams } from "react-router-dom";

function ShowSurveyResponses() {
    const { environmentId, surveyId } = useParams();
    const { data, isLoading, error } = useFormbricks();

    if (isLoading) {
        return <div>Loading...</div>;
    }

    if (error) {
        return <div>Error: {error.message}</div>;
    }

    return (
        <div className="flex-1 min-h-0 w-full flex flex-col">
            <iframe className="flex-1 min-h-0 w-full" src={`https://formbricks-production-7090.up.railway.app/auth/external?jwt=${data?.token}&callbackUrl=https://formbricks-production-7090.up.railway.app/environments/${environmentId}/surveys/${surveyId}/summary`}></iframe>
        </div>
    )
}

export default ShowSurveyResponses;