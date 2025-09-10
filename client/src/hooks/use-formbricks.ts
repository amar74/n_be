import { useQuery } from "@tanstack/react-query";
import { createApiClient as createFormbricksApi } from "@/types/generated/formbricks";
import { apiClient } from "@/services/api/client";

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