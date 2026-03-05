// FilmDto.ts
export interface FilmDto {
    id: string;
    title: string;
    description: string;
}

// IFilmRepository.ts
export interface IFilmRepository {
    getAllFilms(): Promise<FilmDto[]>;
}

// IAuthService.ts
export interface IAuthService {
    isAuthenticated(userId: string): boolean;
    hasPermission(userId: string, permission: string): boolean;
}

// Result.ts
export class Result<T> {
    public isSuccess: boolean;
    public error?: string;
    public value?: T;

    private constructor(isSuccess: boolean, error?: string, value?: T) {
        this.isSuccess = isSuccess;
        this.error = error;
        this.value = value;
    }

    public static ok<T>(value: T): Result<T> {
        return new Result<T>(true, undefined, value);
    }

    public static fail<T>(error: string): Result<T> {
        return new Result<T>(false, error);
    }
}

// ManageFilmListUseCase.ts
import { IFilmRepository } from './IFilmRepository';
import { IAuthService } from './IAuthService';
import { FilmDto } from './FilmDto';
import { Result } from './Result';

export class ManageFilmListUseCase {
    private filmRepository: IFilmRepository;
    private authService: IAuthService;

    constructor(filmRepository: IFilmRepository, authService: IAuthService) {
        this.filmRepository = filmRepository;
        this.authService = authService;
    }

    /**
     * Executes the use case to manage the film list.
     * @param userId - The ID of the user requesting the film list.
     * @returns Result containing the list of films or an error message.
     */
    public async execute(userId: string): Promise<Result<FilmDto[]>> {
        if (!this.authService.isAuthenticated(userId)) {
            return Result.fail<FilmDto[]>('User is not authenticated.');
        }

        if (!this.authService.hasPermission(userId, 'manage_films')) {
            return Result.fail<FilmDto[]>('User does not have permission to manage films.');
        }

        try {
            const films = await this.filmRepository.getAllFilms();
            return Result.ok(films);
        } catch (error) {
            return Result.fail<FilmDto[]>('An error occurred while retrieving the film list.');
        }
    }
}