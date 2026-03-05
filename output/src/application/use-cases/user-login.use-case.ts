// UserLoginUseCase.ts

import { IUserRepository } from '../repositories/IUserRepository';
import { UserLoginDto } from '../dtos/UserLoginDto';
import { Result } from '../utils/Result';
import { User } from '../entities/User';
import { InvalidCredentialsError, UserNotActiveError } from '../errors';

export class UserLoginUseCase {
    private userRepository: IUserRepository;

    constructor(userRepository: IUserRepository) {
        this.userRepository = userRepository;
    }

    /**
     * Executes the user login process
     * @param {UserLoginDto} loginDto - The login credentials
     * @returns {Promise<Result<User>>} - The result of the login operation
     */
    async execute(loginDto: UserLoginDto): Promise<Result<User>> {
        // Validate input
        const validationResult = this.validateInput(loginDto);
        if (!validationResult.isSuccess) {
            return Result.fail(validationResult.error);
        }

        // Step 1: Retrieve user by username
        const user = await this.userRepository.findByUsername(loginDto.username);
        if (!user) {
            return Result.fail(new InvalidCredentialsError('Invalid username or password.'));
        }

        // Step 2: Validate the user's credentials
        const isPasswordValid = await this.userRepository.validatePassword(user, loginDto.password);
        if (!isPasswordValid) {
            return Result.fail(new InvalidCredentialsError('Invalid username or password.'));
        }

        // Step 3: Check if user is active
        if (!user.isActive) {
            return Result.fail(new UserNotActiveError('User account is not active.'));
        }

        // Postconditions: User is logged in successfully
        return Result.ok(user);
    }

    /**
     * Validates the input for login
     * @param {UserLoginDto} loginDto - The login credentials
     * @returns {Result<void>} - The result of the validation
     */
    private validateInput(loginDto: UserLoginDto): Result<void> {
        if (!loginDto.username || loginDto.username.length < 1 || loginDto.username.length > 16) {
            return Result.fail(new Error('Username must be between 1 and 16 characters.'));
        }
        if (!loginDto.password) {
            return Result.fail(new Error('Password must not be empty.'));
        }
        return Result.ok();
    }
}