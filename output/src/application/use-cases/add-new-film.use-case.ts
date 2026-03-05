// FilmDto.ts
export interface FilmDto {
    title: string;
    replacementCost: number;
}

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

// IFilmRepository.ts
export interface IFilmRepository {
    addFilm(film: FilmDto): Promise<void>;
}

// IAuthorizationService.ts
export interface IAuthorizationService {
    isAuthenticated(userId: string): boolean;
    hasPermission(userId: string, permission: string): boolean;
}

// AddNewFilmUseCase.ts
import { FilmDto } from './FilmDto';
import { Result } from './Result';
import { IFilmRepository } from './IFilmRepository';
import { IAuthorizationService } from './IAuthorizationService';

export class AddNewFilmUseCase {
    private filmRepository: IFilmRepository;
    private authorizationService: IAuthorizationService;

    constructor(filmRepository: IFilmRepository, authorizationService: IAuthorizationService) {
        this.filmRepository = filmRepository;
        this.authorizationService = authorizationService;
    }

    /**
     * Executes the use case to add a new film.
     * @param userId The ID of the user performing the action.
     * @param filmDto The film details to add.
     * @returns Result indicating success or failure.
     */
    public async execute(userId: string, filmDto: FilmDto): Promise<Result<void>> {
        if (!this.authorizationService.isAuthenticated(userId)) {
            return Result.fail('User is not authenticated.');
        }

        if (!this.authorizationService.hasPermission(userId, 'add_film')) {
            return Result.fail('User does not have permission to add films.');
        }

        const validationError = this.validateFilm(filmDto);
        if (validationError) {
            return Result.fail(validationError);
        }

        try {
            await this.filmRepository.addFilm(filmDto);
            return Result.ok();
        } catch (error) {
            return Result.fail('An error occurred while adding the film: ' + error.message);
        }
    }

    /**
     * Validates the film details.
     * @param filmDto The film details to validate.
     * @returns A string error message if validation fails, otherwise undefined.
     */
    private validateFilm(filmDto: FilmDto): string | undefined {
        if (!filmDto.title || filmDto.title.length < 1 || filmDto.title.length > 128) {
            return 'Film title must not be null and must have valid size.';
        }

        if (filmDto.replacementCost == null) {
            return 'Replacement cost must be specified.';
        }

        return undefined;
    }
}