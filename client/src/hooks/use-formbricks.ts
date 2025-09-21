import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { createApiClient as createFormbricksApi, schemas } from "@/types/generated/formbricks";
import { apiClient } from "@/services/api/client";
import type { z } from "zod";

const formbricksApi = createFormbricksApi(import.meta.env.VITE_API_BASE_URL, {
    axiosInstance: apiClient,
});

export function useFormbricks() {
    const { data, isLoading, error } = useQuery({
        queryKey: ['formbricks'],
        queryFn: () => formbricksApi.getFormbricksLoginToken(),
    });
    return { data, isLoading, error };
}
export function useFormbricksSurveys() {
    const qc = useQueryClient();

    const { data, isLoading, error } = useQuery({
        queryKey: ['formbricksSurveys'],
        queryFn: () => formbricksApi.getFormbricksSurveys(),
    });
    type Survey = z.infer<typeof schemas.Survey>;
    type SurveyCreateRequest = { name: string };

    const { mutateAsync: createSurvey, isPending: creating, error: createError } = useMutation({
        mutationFn: async (payload: SurveyCreateRequest): Promise<Survey> => {
            const res = await apiClient.post('/formbricks/surveys', payload);
            return res.data as Survey;
        },
        onSuccess: async () => {
            await qc.invalidateQueries({ queryKey: ['formbricksSurveys'] });
        },
    });

    type SurveyLinkResponse = { url: string };

    const { mutateAsync: createSurveyLink, isPending: linking, error: linkError } = useMutation({
        mutationFn: async (args: { surveyId: string; email: string }): Promise<SurveyLinkResponse> => {
            const res = await apiClient.post(`/formbricks/surveys/${args.surveyId}/link`, { email: args.email });
            return res.data as SurveyLinkResponse;
        },
    });

    return { data, isLoading, error, createSurvey, creating, createError, createSurveyLink, linking, linkError };
}