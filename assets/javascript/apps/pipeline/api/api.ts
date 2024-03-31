import axios, {AxiosInstance} from "axios";
import {PipelineType} from "../types/pipeline";

class ApiClient {
  private team: string | null;
  constructor() {
    this.team = null;
  }

  setTeam(team: string) {
    this.team = team;
  }

  public async updatePipeline(
    pipelineId: number,
    updatedPipeline: PipelineType
  ): Promise<PipelineType> {
    const client = this.createClient()
    try {
      const response = await client.post(`/pipelines/${pipelineId}/`, updatedPipeline);

      if (response?.status !== 200) {
        throw new Error(`HTTP error! status: ${response?.status}`);
      }
      return response.data;
    } catch (error) {
      console.error(error);
      throw error;
    }
  }

  public async getPipeline(pipelineId: number): Promise<PipelineType> {
    const client = this.createClient()
    try {
      const response = await client.get(`/pipelines/${pipelineId}`);
      if (response.status !== 200) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }
      return response.data;
    } catch (error) {
      console.error(error);
      throw error;
    }
  }

  private createClient(): AxiosInstance {
    return axios.create({
      baseURL: `/a/${this.team}`,
    });
  }
}

export const apiClient = new ApiClient()
