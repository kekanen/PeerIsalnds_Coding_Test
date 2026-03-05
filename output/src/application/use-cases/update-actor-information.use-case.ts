// Result.ts
export class Result<T> {
    public isSuccess: boolean;
    public error?: string;
    public value?: T;

    private constructor(isSuccess: boolean, value?: T, error?: string) {
        this.isSuccess = isSuccess;
        this.value = value;
        this.error = error;
    }

    public static ok<T>(value?: T): Result<T> {
        return new Result<T>(true, value);
    }

    public static fail<T>(error: string): Result<T> {
        return new Result<T>(false, undefined, error);
    }
}

// ActorDto.ts
export interface ActorDto {
    id: string;
    name: string;
    age: number;
    active: boolean;
}

// IActorRepository.ts
export interface IActorRepository {
    updateActor(actor: ActorDto): Promise<void>;
    findActorById(id: string): Promise<ActorDto | null>;
}

// IAuthService.ts
export interface IAuthService {
    isAuthenticated(): boolean;
    hasPermission(permission: string): boolean;
}

// UpdateActorInformationUseCase.ts
import { Result } from './Result';
import { ActorDto } from './ActorDto';
import { IActorRepository } from './IActorRepository';
import { IAuthService } from './IAuthService';

export class UpdateActorInformationUseCase {
    private actorRepository: IActorRepository;
    private authService: IAuthService;

    constructor(actorRepository: IActorRepository, authService: IAuthService) {
        this.actorRepository = actorRepository;
        this.authService = authService;
    }

    /**
     * Executes the use case to update actor information.
     * @param actorDto The updated actor information.
     * @returns Result indicating success or failure.
     */
    public async execute(actorDto: ActorDto): Promise<Result<void>> {
        // Validate preconditions
        if (!this.authService.isAuthenticated()) {
            return Result.fail('User is not authenticated.');
        }

        if (!this.authService.hasPermission('update_actors')) {
            return Result.fail('User does not have permission to update actors.');
        }

        // Validate input
        if (!actorDto.id || !actorDto.name || actorDto.age < 0) {
            return Result.fail('Invalid actor information provided.');
        }

        // Business rule: Active status must be true for updates
        if (!actorDto.active) {
            return Result.fail('Actor must be active to update information.');
        }

        // Check if actor exists
        const existingActor = await this.actorRepository.findActorById(actorDto.id);
        if (!existingActor) {
            return Result.fail('Actor not found.');
        }

        // Update actor information
        try {
            await this.actorRepository.updateActor(actorDto);
            return Result.ok();
        } catch (error) {
            return Result.fail('Failed to update actor information: ' + error.message);
        }
    }
}