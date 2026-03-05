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

    public static success<T>(value: T): Result<T> {
        return new Result<T>(true, value);
    }

    public static failure<T>(error: string): Result<T> {
        return new Result<T>(false, undefined, error);
    }
}

// ActorDto.ts
export interface ActorDto {
    name: string;
    age: number;
    authorityId: string;
    isActive: boolean;
}

// IActorRepository.ts
export interface IActorRepository {
    add(actor: ActorDto): Promise<void>;
}

// IAuthenticationService.ts
export interface IAuthenticationService {
    isAuthenticated(): boolean;
    hasPermission(permission: string): boolean;
}

// AddNewActorUseCase.ts
import { Result } from './Result';
import { ActorDto } from './ActorDto';
import { IActorRepository } from './IActorRepository';
import { IAuthenticationService } from './IAuthenticationService';

export class AddNewActorUseCase {
    private actorRepository: IActorRepository;
    private authService: IAuthenticationService;

    constructor(actorRepository: IActorRepository, authService: IAuthenticationService) {
        this.actorRepository = actorRepository;
        this.authService = authService;
    }

    /**
     * Executes the use case to add a new actor.
     * @param actorDto The details of the actor to be added.
     * @returns Result indicating success or failure.
     */
    public async execute(actorDto: ActorDto): Promise<Result<void>> {
        // Validate preconditions
        if (!this.authService.isAuthenticated()) {
            return Result.failure('User is not authenticated.');
        }

        if (!this.authService.hasPermission('add_actor')) {
            return Result.failure('User does not have permission to add actors.');
        }

        // Validate input
        const validationError = this.validateActorDto(actorDto);
        if (validationError) {
            return Result.failure(validationError);
        }

        // Execute business logic
        try {
            await this.actorRepository.add(actorDto);
            return Result.success(undefined);
        } catch (error) {
            return Result.failure('Failed to add new actor: ' + error.message);
        }
    }

    /**
     * Validates the actor DTO.
     * @param actorDto The actor DTO to validate.
     * @returns A validation error message or undefined if valid.
     */
    private validateActorDto(actorDto: ActorDto): string | undefined {
        if (!actorDto.name || actorDto.name.length < 1 || actorDto.name.length > 16) {
            return 'Actor name must be between 1 and 16 characters.';
        }
        if (!actorDto.authorityId) {
            return 'Authority ID must not be null.';
        }
        if (!actorDto.isActive) {
            return 'Active status must be true for actors.';
        }
        return undefined;
    }
}