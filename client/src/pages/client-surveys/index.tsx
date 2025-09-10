import { useFormbricks } from "@/hooks/use-formbricks";

function ClientSurveys() {
    const { data, isLoading, error } = useFormbricks();

    if (isLoading) {
        return <div>Loading...</div>;
    }

    if (error) {
        return <div>Error: {error.message}</div>;
    }

    return (
        <div className="flex-1 min-h-0 w-full flex flex-col">
            <iframe className="flex-1 min-h-0 w-full" src={`http://localhost:3000/auth/external?jwt=${data?.token}`}></iframe>
        </div>
    )
}

export default ClientSurveys;