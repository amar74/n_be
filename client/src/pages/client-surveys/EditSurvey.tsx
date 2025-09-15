import { useFormbricks } from "@/hooks/use-formbricks";
import { useParams } from "react-router-dom";

function EditSurvey() {
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
            <iframe className="flex-1 min-h-0 w-full" src={`http://localhost:3000/auth/external?jwt=${data?.token}&callbackUrl=http://localhost:3000/environments/${environmentId}/surveys/${surveyId}/edit`}></iframe>
        </div>
    )
}

export default EditSurvey;