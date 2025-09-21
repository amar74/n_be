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
        <div className="w-full h-screen flex flex-col">
            <iframe className="w-full flex-1 min-h-0 border-0" src={`https://formbricks-production-7090.up.railway.app/auth/external?jwt=${data?.token}&callbackUrl=https://formbricks-production-7090.up.railway.app/environments/${environmentId}/surveys/${surveyId}/summary`}></iframe>
            {/* <iframe className="w-full flex-1 min-h-0 border-0" src={`https://formbricks-production-7090.up.railway.app/auth/external?jwt=${data?.token}`}></iframe> */}
        </div>
    )
}

export default ShowSurveyResponses;